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


def scorecard(cfg: Config, conn: sqlite3.Connection, now: datetime) -> str:
    df = load_signals(conn)
    min_conf = cfg.report["min_confidence"]
    need = cfg.report["gate1_min_calls"]
    out = [f"# newsdesk scorecard", "", f"Generated {now:%Y-%m-%d %H:%M} UTC.", ""]
    if df.empty:
        return "\n".join(out + ["No calls logged yet. Run `python -m newsdesk run` first."])

    counts = df["status"].value_counts().to_dict()
    out += [
        "## Log",
        "",
        f"- Calls logged: {len(df)} since {df['created_at'].min()[:10]}",
        f"- \"No trade\" calls: {counts.get('skipped', 0)}",
        f"- Waiting for their exit session: {counts.get('pending', 0)}",
        f"- Scored: {counts.get('scored', 0)}",
        f"- Could not be scored: {counts.get('error', 0)}",
        "",
    ]
    sc = df[df["status"] == "scored"].copy()
    acted = sc[sc["confidence"] >= min_conf]
    s = stats(acted)

    out += ["## Gate 1", "",
            f"Calls you would act on are those with confidence {min_conf} or higher. "
            f"Gate 1 needs at least {need} of them, and on average they must beat simply "
            "holding the index over the same days, after costs, by a margin unlikely "
            "to be luck (t-stat above 2).", ""]
    if s["n"] < need:
        verdict = f"**Not decided yet.** {s['n']} of {need} calls scored."
    elif s["vs_hold"] > 0 and s["t"] > 2:
        verdict = "**Passed.** Move on to Phase 2 (paper trading)."
    else:
        verdict = "**Failed.** The calls did not beat holding the index after costs. Stop the trading idea here."
    out += [verdict, ""]
    if s["n"]:
        out += [HEADER, _row(f"Confidence ≥ {min_conf}", s), ""]
        out += [f"Right-way rate: {s['right_way'] * 100:.1f}% "
                f"(chance of doing this well by coin-flipping: {s['p_right_way']:.3f}). "
                f"Worst single call {_pct(s['worst'])}, best {_pct(s['best'])}.", ""]

    if not sc.empty:
        out += ["## Breakdown (all scored calls)", "", HEADER]
        out.append(_row("All", stats(sc)))
        for col, label in [("direction", "Direction"), ("confidence", "Confidence"),
                           ("horizon_days", "Horizon (sessions)")]:
            for v, g in sc.groupby(col):
                out.append(_row(f"{label}: {v}", stats(g)))
        sc["region"] = sc["symbol"].map(lambda x: cfg.market_for(x).region)
        for v, g in sc.groupby("region"):
            out.append(_row(f"Region: {v}", stats(g)))
        out.append("")

        # Baseline: buy every stock that had a call, same windows, long only.
        rt = sc.apply(lambda r: round_trip_cost(
            cfg.scoring["costs"][cfg.market_for(r["symbol"]).region],
            cfg.scoring["position_size_eur"]), axis=1)
        base = (sc["stock_return"] - rt).mean()
        out += ["## Baseline", "",
                f"Buying every stock that had a call, ignoring the AI's direction, "
                f"same days and costs: {_pct(base)} average per trade. The AI is only "
                "useful if its calls do better than this.", ""]

    out += ["## Caveats", "",
            "- Calls that overlap in time are not independent, so the t-stat overstates certainty. Treat 2 as a minimum, not proof.",
            "- Costs are estimates from config.yaml. Real Interactive Brokers fills will differ.",
            "- Entry is the next session's open after the call, exit the close of the last session in the horizon.",
            ""]
    return "\n".join(out)


def brief(conn: sqlite3.Connection, now: datetime, hours: float = 24) -> str:
    since = (now - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        "SELECT * FROM signals WHERE created_at >= ? ORDER BY"
        " CASE direction WHEN 'none' THEN 1 ELSE 0 END, confidence DESC, created_at DESC",
        (since,),
    ).fetchall()
    out = [f"# News brief, last {hours:g} hours", "", f"Generated {now:%Y-%m-%d %H:%M} UTC.", ""]
    calls = [r for r in rows if r["direction"] != "none"]
    quiet = [r for r in rows if r["direction"] == "none"]
    if not rows:
        return "\n".join(out + ["No calls in this period."])
    for r in calls:
        out += [f"## {r['symbol']}: {r['direction'].upper()}, confidence {r['confidence']}/5, "
                f"{r['horizon_days']} session(s)", "",
                f"- **What happened:** {r['summary']}",
                f"- **Why:** {r['rationale']}",
                f"- **Wrong if:** {r['invalidation']}",
                f"- Logged {r['created_at'][:16].replace('T', ' ')} UTC", ""]
    if quiet:
        out += ["## No trade", ""]
        out += [f"- **{r['symbol']}:** {r['summary']}" for r in quiet]
        out.append("")
    out.append("_Research log, not advice. Calls are scored automatically; check the scorecard before acting on any of them._")
    return "\n".join(out)
