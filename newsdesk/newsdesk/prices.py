"""Daily prices from Yahoo Finance and the session arithmetic used for scoring."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

import pandas as pd

from .config import Market


@lru_cache(maxsize=256)
def _history(symbol: str, start: date, end: date) -> pd.DataFrame:
    import yfinance as yf

    df = yf.Ticker(symbol).history(
        start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
        interval="1d", auto_adjust=True,
    )
    if df.empty:
        return pd.DataFrame(columns=["Open", "Close"])
    # Index is tz-aware in the exchange's time zone; keep the session date.
    df.index = [ts.date() for ts in df.index]
    return df[["Open", "Close"]].dropna()


def daily_bars(symbol: str, start: date, end: date) -> pd.DataFrame:
    """Dividend- and split-adjusted Open/Close indexed by session date."""
    return _history(symbol, start, end).copy()


def local_now(market: Market, now_utc: datetime) -> datetime:
    return now_utc.astimezone(ZoneInfo(market.tz))


def entry_session(created_at: datetime, market: Market, sessions: list[date]) -> date | None:
    """First session whose opening auction comes after the call was logged.

    A call logged before today's open enters at today's open; one logged during
    or after the session enters at the next session's open. This throws away
    any move between the call and the next open, which is the honest choice:
    a person has to read and approve the call before it can be traded."""
    local = created_at.astimezone(ZoneInfo(market.tz))
    hh, mm = (int(x) for x in market.open.split(":"))
    for d in sorted(sessions):
        if d > local.date() or (d == local.date() and local.time() < time(hh, mm)):
            return d
    return None


def exit_session(entry: date, horizon_days: int, sessions: list[date]) -> date | None:
    """Session `horizon_days` counting the entry session as 1."""
    s = sorted(sessions)
    i = s.index(entry) + horizon_days - 1
    return s[i] if i < len(s) else None


def price_context(symbol: str, today: date) -> str | None:
    """One line of recent price action to give the analyst some context."""
    try:
        df = daily_bars(symbol, today - timedelta(days=14), today)
    except Exception:
        return None
    if len(df) < 2:
        return None
    closes = df["Close"]
    last = closes.iloc[-1]
    d1 = last / closes.iloc[-2] - 1
    d5 = last / closes.iloc[max(0, len(closes) - 6)] - 1
    return (f"Last close {last:.2f} on {df.index[-1]}; "
            f"1-session change {d1:+.1%}; 5-session change {d5:+.1%}.")
