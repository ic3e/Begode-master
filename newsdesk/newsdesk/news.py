"""Collect recent headlines per stock from Google News RSS and Yahoo Finance."""
from __future__ import annotations

import calendar
import hashlib
import html
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

from .config import Config, Stock

log = logging.getLogger(__name__)


@dataclass
class NewsItem:
    symbol: str
    title: str
    source: str | None
    url: str | None
    summary: str | None
    published_at: datetime | None

    @property
    def id(self) -> str:
        return news_id(self.symbol, self.title)


def normalise_title(title: str) -> str:
    title = re.sub(r"\s+-\s+[^-]{2,60}$", "", title.strip())  # drop " - Publisher"
    title = re.sub(r"[^a-z0-9 ]+", " ", title.lower())
    return re.sub(r"\s+", " ", title).strip()


def news_id(symbol: str, title: str) -> str:
    return hashlib.sha1(f"{symbol}|{normalise_title(title)}".encode()).hexdigest()[:16]


def _clean(text: str | None, limit: int = 400) -> str | None:
    if not text:
        return None
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] or None


# ---------------------------------------------------------------- Google News
def google_news_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + quote_plus(f"{query} when:2d")
        + "&hl=en-US&gl=US&ceid=US:en"
    )


def parse_google_news(symbol: str, feed) -> list[NewsItem]:
    """`feed` is the object returned by feedparser.parse()."""
    items = []
    for e in feed.entries:
        published = None
        if getattr(e, "published_parsed", None):
            published = datetime.fromtimestamp(
                calendar.timegm(e.published_parsed), tz=timezone.utc
            )
        source = None
        if getattr(e, "source", None) is not None:
            source = getattr(e.source, "title", None) or e.source.get("title")
        summary = _clean(getattr(e, "summary", None))
        if summary and normalise_title(summary).startswith(normalise_title(e.title)):
            summary = None  # Google often repeats the headline as the summary
        items.append(
            NewsItem(symbol, e.title.strip(), source, getattr(e, "link", None),
                     summary, published)
        )
    return items


def fetch_google_news(stock: Stock) -> list[NewsItem]:
    import feedparser

    feed = feedparser.parse(google_news_url(stock.search_query))
    if feed.get("bozo") and not feed.entries:
        raise RuntimeError(f"Google News feed failed: {feed.get('bozo_exception')}")
    return parse_google_news(stock.symbol, feed)


# --------------------------------------------------------------------- Yahoo
def parse_yahoo_news(symbol: str, raw: list[dict]) -> list[NewsItem]:
    items = []
    for r in raw or []:
        c = r.get("content") if isinstance(r.get("content"), dict) else None
        if c:  # format used by yfinance since 2025
            title = c.get("title")
            published = None
            if c.get("pubDate"):
                published = datetime.fromisoformat(c["pubDate"].replace("Z", "+00:00"))
            url = (c.get("canonicalUrl") or {}).get("url") or (
                c.get("clickThroughUrl") or {}
            ).get("url")
            source = (c.get("provider") or {}).get("displayName")
            summary = _clean(c.get("summary"))
        else:  # older format
            title = r.get("title")
            ts = r.get("providerPublishTime")
            published = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
            url, source, summary = r.get("link"), r.get("publisher"), None
        if title:
            items.append(NewsItem(symbol, title.strip(), source, url, summary, published))
    return items


def fetch_yahoo_news(stock: Stock) -> list[NewsItem]:
    import yfinance as yf

    return parse_yahoo_news(stock.symbol, yf.Ticker(stock.symbol).news)


FETCHERS = {"google_news": fetch_google_news, "yahoo": fetch_yahoo_news}


# ------------------------------------------------------------------- storing
def select_recent(items: list[NewsItem], now: datetime, lookback_hours: float,
                  limit: int) -> list[NewsItem]:
    """Keep items published inside the lookback window, newest first, one per
    normalised headline. Items with no publish time are dropped: we cannot tell
    whether they are news or an old story resurfacing."""
    cutoff = now - timedelta(hours=lookback_hours)
    seen, out = set(), []
    for it in sorted(items, key=lambda i: i.published_at or now, reverse=True):
        if it.published_at is None or not (cutoff <= it.published_at <= now + timedelta(minutes=10)):
            continue
        if it.id in seen:
            continue
        seen.add(it.id)
        out.append(it)
    return out[:limit]


def store(conn: sqlite3.Connection, items: list[NewsItem], now: datetime) -> int:
    """Insert items not seen before. Returns how many were new."""
    new = 0
    for it in items:
        cur = conn.execute(
            "INSERT OR IGNORE INTO news (id, symbol, title, source, url, summary,"
            " published_at, fetched_at) VALUES (?,?,?,?,?,?,?,?)",
            (it.id, it.symbol, it.title, it.source, it.url, it.summary,
             it.published_at.isoformat() if it.published_at else None,
             now.isoformat()),
        )
        new += cur.rowcount
    conn.commit()
    return new


def collect(cfg: Config, conn: sqlite3.Connection, now: datetime,
            stocks: list[Stock] | None = None) -> dict[str, int]:
    """Fetch every source for every stock; return new-item counts per symbol."""
    counts = {}
    for stock in stocks or cfg.stocks:
        items: list[NewsItem] = []
        for name in cfg.news["sources"]:
            try:
                items += FETCHERS[name](stock)
            except Exception as exc:  # one bad source must not stop the run
                log.warning("%s: %s failed: %s", stock.symbol, name, exc)
        recent = select_recent(items, now, cfg.news["lookback_hours"],
                               cfg.news["max_items_per_ticker"])
        counts[stock.symbol] = store(conn, recent, now)
    return counts
