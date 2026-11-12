"""Score logged calls against what the prices actually did."""
from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from .config import Config
from . import prices

log = logging.getLogger(__name__)


def round_trip_cost(costs: dict, position_eur: float) -> float:
    """Commission on both sides (with its minimum), plus spread and FX, as a fraction."""
    side = max(costs["commission_pct"] / 100 * position_eur,
               costs["commission_min_eur"]) / position_eur
    return 2 * side + (costs["spread_bps"] + costs["fx_bps"]) / 1e4


def borrow_cost(annual_pct: float, entry: date, exit: date) -> float:
    days = (exit - entry).days + 1
    return annual_pct / 100 * days / 365


@dataclass
class Outcome:
    stock_return: float
    bench_return: float | None
    gross_return: float
    cost: float
    net_return: float
    net_excess: float | None


def outcome(direction: str, entry: float, exit: float, bench_entry: float | None,
            bench_exit: float | None, cost: float) -> Outcome:
    """`gross` is the stock's move signed by direction. `net_excess` is the
    market-neutral view: the call's edge over the index after costs."""
    sign = {"long": 1, "short": -1}[direction]
    stock_ret = exit / entry - 1
    bench_ret = (bench_exit / bench_entry - 1) if bench_entry and bench_exit else None
    gross = sign * stock_ret
    net = gross - cost
    excess = sign * (stock_ret - bench_ret) - cost if bench_ret is not None else None
    return Outcome(stock_ret, bench_ret, gross, cost, net, excess)


def _bench_prices(bench_bars, entry: date, exit: date):
    """Benchmark open on the entry session and close on the exit session; if a
    holiday differs between exchanges, use the nearest session inside the window."""
    if bench_bars is None or bench_bars.empty:
        return None, None
    inside = bench_bars[(bench_bars.index >= entry) & (bench_bars.index <= exit)]
    if inside.empty:
        return None, None
    return float(inside["Open"].iloc[0]), float(inside["Close"].iloc[-1])


def score_pending(cfg: Config, conn: sqlite3.Connection, now: datetime,
                  bars=prices.daily_bars) -> dict[str, int]:
    """Fill in outcomes for calls whose exit session has closed."""
    counts = {"scored": 0, "waiting": 0, "error": 0}
    sc = cfg.scoring
    rows = conn.execute("SELECT * FROM signals WHERE status='pending'").fetchall()
    for r in rows:
        market = cfg.market_for(r["symbol"])
        created = datetime.fromisoformat(r["created_at"])
        today = prices.local_now(market, now).date()
        start = created.date() - timedelta(days=3)
        try:
            df = bars(r["symbol"], start, today)
        except Exception as e:
            log.warning("%s: price fetch failed: %s", r["symbol"], e)
            counts["waiting"] += 1
            continue
        sessions = list(df.index)
        entry = prices.entry_session(created, market, sessions)
        exit_ = prices.exit_session(entry, r["horizon_days"], sessions) if entry else None
        if entry is None or exit_ is None or exit_ >= today:
            if now - created > timedelta(days=30):
                conn.execute("UPDATE signals SET status='error', note=? WHERE id=?",
                             ("No price data 30 days after the call", r["id"]))
                counts["error"] += 1
            else:
                counts["waiting"] += 1
            continue
        try:
            bdf = bars(market.benchmark, start, today)
        except Exception as e:
            log.warning("%s: benchmark fetch failed: %s", market.benchmark, e)
            bdf = None
        b_entry, b_exit = _bench_prices(bdf, entry, exit_)
        entry_px = float(df.loc[entry, "Open"])
        exit_px = float(df.loc[exit_, "Close"])
        cost = round_trip_cost(sc["costs"][market.region], sc["position_size_eur"])
        if r["direction"] == "short":
            cost += borrow_cost(sc["short_borrow_annual_pct"], entry, exit_)
        o = outcome(r["direction"], entry_px, exit_px, b_entry, b_exit, cost)
        conn.execute(
            "UPDATE signals SET status='scored', entry_date=?, exit_date=?, entry_price=?,"
            " exit_price=?, benchmark=?, bench_entry=?, bench_exit=?, stock_return=?,"
            " bench_return=?, gross_return=?, cost=?, net_return=?, net_excess=?,"
            " scored_at=? WHERE id=?",
            (entry.isoformat(), exit_.isoformat(), entry_px, exit_px, market.benchmark,
             b_entry, b_exit, o.stock_return, o.bench_return, o.gross_return, o.cost,
             o.net_return, o.net_excess, now.astimezone(timezone.utc).isoformat(),
             r["id"]),
        )
        counts["scored"] += 1
    conn.commit()
    return counts
