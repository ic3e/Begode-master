"""Turn the signal log into a scorecard and a daily brief (Markdown)."""
from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timedelta

import pandas as pd

from .config import Config
from .scoring import round_trip_cost


def binom_p_greater(k: int, n: int, p: float = 0.5) -> float:
    """One-sided P(X >= k) for X ~ Binomial(n, p)."""
    if n == 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                          + i * math.log(p) + (n - i) * math.log(1 - p))
    return min(1.0, total)


def stats(df: pd.DataFrame) -> dict:
    n = len(df)
    if n == 0:
        return {"n": 0}
    vs_hold = (df["net_return"] - df["bench_return"]).dropna()
    right = int((df["net_excess"] + df["cost"] > 0).sum())  # beat the index, before costs
    sd = vs_hold.std(ddof=1) if len(vs_hold) > 1 else float("nan")
    return {
        "n": n,
        "net": df["net_return"].mean(),
        "bench": df["bench_return"].mean(),
        "vs_hold": vs_hold.mean() if len(vs_hold) else float("nan"),
        "t": vs_hold.mean() / (sd / math.sqrt(len(vs_hold))) if sd and sd > 0 else float("nan"),
        "profitable": (df["net_return"] > 0).mean(),
        "right_way": right / n,
        "p_right_way": binom_p_greater(right, n),
        "worst": df["net_return"].min(),
        "best": df["net_return"].max(),
    }


def _pct(x, digits=2):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:+.{digits}f}%"


def _row(label: str, s: dict) -> str:
    if s["n"] == 0:
        return f"| {label} | 0 | | | | | | |"
    return (f"| {label} | {s['n']} | {_pct(s['net'])} | {_pct(s['bench'])} | "
            f"{_pct(s['vs_hold'])} | {s['t']:.2f} | {s['profitable'] * 100:.0f}% | "
            f"{s['right_way'] * 100:.0f}% |")


HEADER = ("| Group | Calls | Avg net return | Index, same days | Ahead of holding the index | t-stat | Profitable | Right way vs index |\n"
          "|---|---:|---:|---:|---:|---:|---:|---:|")


def load_signals(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM signals", conn)


def gate_verdict(s: dict, need: int) -> str:
    if s["n"] < need:
        return f"Not decided yet ({s['n']} of {need} calls scored)"
    if s["vs_hold"] > 0 and s["t"] > 2:
        return "Passed"
    return "Failed"


def scorecard(cfg: Config, conn: sqlite3.Connection, now: datetime) -> str:
    df = load_signals(conn)
    min_conf = cfg.report["min_confidence"]
    need = cfg.report["gate1_min_calls"]
    out = ["# newsdesk scorecard", "", f"Generated {now:%Y-%m-%d %H:%M} UTC.", ""]
    if df.empty:
        return "\n".join(out + ["No calls logged yet. Run `python -m newsdesk run` first."])

    analysts = sorted(df["analyst"].unique())
    out += ["## Log", "",
            "| Analyst | Model | Calls logged | No trade | Waiting | Scored | Unscorable |",
            "|---|---|---:|---:|---:|---:|---:|"]
    for a in analysts:
        g = df[df["analyst"] == a]
        c = g["status"].value_counts().to_dict()
        models = ", ".join(sorted(g["model"].dropna().unique()))
        out.append(f"| {a} | {models} | {len(g)} | {c.get('skipped', 0)} | "
                   f"{c.get('pending', 0)} | {c.get('scored', 0)} | {c.get('error', 0)} |")
    out += ["", f"First call {df['created_at'].min()[:10]}.", ""]

    sc = df[df["status"] == "scored"].copy()
    out += ["## Gate 1", "",
            f"Calls you would act on are those with confidence {min_conf} or higher. "
            f"An analyst passes Gate 1 with at least {need} such calls that on average "
            "beat simply holding the index over the same days, after costs, by a margin "
            "unlikely to be luck (t-stat above 2). If no analyst passes, stop the trading "
            "idea here.", "",
            "| Analyst | Result |", "|---|---|"]
    gate_stats = {}
    for a in analysts:
        s = stats(sc[(sc["analyst"] == a) & (sc["confidence"] >= min_conf)])
        gate_stats[a] = s
        out.append(f"| {a} | **{gate_verdict(s, need)}** |")
    out.append("")
    if any(s["n"] for s in gate_stats.values()):
        out += [HEADER] + [_row(a, s) for a, s in gate_stats.items() if s["n"]] + [""]
        for a, s in gate_stats.items():
            if s["n"]:
                out.append(f"- **{a}:** right way {s['right_way'] * 100:.1f}% of the time "
                           f"(chance of doing this well by coin-flipping: {s['p_right_way']:.3f}); "
                           f"worst call {_pct(s['worst'])}, best {_pct(s['best'])}.")
        out.append("")

    if not sc.empty:
        sc["region"] = sc["symbol"].map(lambda x: cfg.market_for(x).region)
        for a in analysts:
            g = sc[sc["analyst"] == a]
            if g.empty:
                continue
            out += [f"## Breakdown: {a} (all scored calls)", "", HEADER, _row("All", stats(g))]
            for col, label in [("direction", "Direction"), ("confidence", "Confidence"),
                               ("horizon_days", "Horizon (sessions)"), ("region", "Region")]:
                for v, gg in g.groupby(col):
                    out.append(_row(f"{label}: {v}", stats(gg)))
            out.append("")

        # Baseline: buy every stock that had a call, same windows, long only.
        rt = sc.apply(lambda r: round_trip_cost(
            cfg.scoring["costs"][cfg.market_for(r["symbol"]).region],
            cfg.scoring["position_size_eur"]), axis=1)
        base = (sc["stock_return"] - rt).mean()
        out += ["## Baseline", "",
                f"Buying every stock that had a call, ignoring the direction, "
                f"same days and costs: {_pct(base)} average per trade. An analyst is only "
                "useful if its calls do better than this.", ""]

    out += ["## Caveats", "",
            "- Calls that overlap in time are not independent, so the t-stat overstates certainty. Treat 2 as a minimum, not proof.",
            "- Costs are estimates from config.yaml. Real Interactive Brokers fills will differ.",
            "- Entry is the next session's open after the call, exit the close of the last session in the horizon.",
            ""]
    return "\n".join(out)


def brief(conn: sqlite3.Connection, now: datetime, hours: float = 24) -> str:
    """Latest call per analyst per stock, stocks with a trade call first."""
    since = (now - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        "SELECT * FROM signals WHERE created_at >= ? ORDER BY created_at DESC", (since,),
    ).fetchall()
    out = [f"# News brief, last {hours:g} hours", "", f"Generated {now:%Y-%m-%d %H:%M} UTC.", ""]
    if not rows:
        return "\n".join(out + ["No calls in this period."])
    latest: dict[str, dict[str, sqlite3.Row]] = {}
    for r in rows:  # newest first, so the first one seen is the latest
        latest.setdefault(r["symbol"], {}).setdefault(r["analyst"], r)
    active = {s: c for s, c in latest.items() if any(r["direction"] != "none" for r in c.values())}
    quiet = {s: c for s, c in latest.items() if s not in active}
    rank = lambda item: -max(r["confidence"] for r in item[1].values() if r["direction"] != "none")
    for symbol, calls in sorted(active.items(), key=rank):
        out += [f"## {symbol}", ""]
        for a, r in sorted(calls.items()):
            if r["direction"] == "none":
                out += [f"**{a}: no trade.** {r['summary']}", ""]
                continue
            out += [f"**{a}: {r['direction'].upper()}, confidence {r['confidence']}/5, "
                    f"{r['horizon_days']} session(s)** "
                    f"(logged {r['created_at'][:16].replace('T', ' ')} UTC)", "",
                    f"- What happened: {r['summary']}",
                    f"- Why: {r['rationale']}",
                    f"- Wrong if: {r['invalidation']}", ""]
        agree = {r["direction"] for r in calls.values()}
        if len(calls) > 1 and len(agree) > 1:
            out += ["_The analysts disagree on this one._", ""]
    if quiet:
        out += ["## No trade", ""]
        out += [f"- **{s}:** {next(iter(c.values()))['summary']}" for s, c in sorted(quiet.items())]
        out.append("")
    out.append("_Research log, not advice. Calls are scored automatically; check the scorecard before acting on any of them._")
    return "\n".join(out)
