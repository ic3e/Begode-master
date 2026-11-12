"""SQLite storage. The signal log is append-only: a call is never edited after
it is written, only its outcome columns are filled in when it is scored."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id            TEXT PRIMARY KEY,      -- hash of symbol + normalised title
    symbol        TEXT NOT NULL,
    title         TEXT NOT NULL,
    source        TEXT,
    url           TEXT,
    summary       TEXT,
    published_at  TEXT,                  -- UTC ISO, as reported by the feed
    fetched_at    TEXT NOT NULL,         -- UTC ISO, when we first saw it
    analysed_at   TEXT                   -- UTC ISO, when it was sent to the AI
);
CREATE INDEX IF NOT EXISTS news_symbol ON news(symbol, analysed_at);

CREATE TABLE IF NOT EXISTS signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT NOT NULL,
    created_at      TEXT NOT NULL,       -- UTC ISO; the call is timestamped here
    direction       TEXT NOT NULL,       -- long | short | none
    horizon_days    INTEGER NOT NULL,
    confidence      INTEGER NOT NULL,    -- 1..5
    summary         TEXT,
    rationale       TEXT,
    invalidation    TEXT,
    news_ids        TEXT,                -- JSON list of news.id
    model           TEXT,
    -- outcome, filled in by `score`
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | scored | skipped | error
    entry_date      TEXT,
    exit_date       TEXT,
    entry_price     REAL,
    exit_price      REAL,
    benchmark       TEXT,
    bench_entry     REAL,
    bench_exit      REAL,
    stock_return    REAL,                -- raw move of the stock, entry to exit
    bench_return    REAL,
    gross_return    REAL,                -- signed by direction
    cost            REAL,
    net_return      REAL,
    net_excess      REAL,                -- net_return minus the benchmark's signed move
    scored_at       TEXT,
    note            TEXT
);
CREATE INDEX IF NOT EXISTS signals_status ON signals(status);
"""


def connect(path: Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
