import json
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import feedparser
import pandas as pd
import pytest

from newsdesk import analyst, config, db, news, prices, report, scoring

UTC = timezone.utc


@pytest.fixture
def cfg(tmp_path):
    c = config.load()
    c.database = tmp_path / "t.db"
    return c


@pytest.fixture
def conn(cfg):
    return db.connect(cfg.database)


# ---------------------------------------------------------------- news
RSS = """<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>
<item><title>Nokia wins 5G deal with Operator - Reuters</title><link>https://a</link>
<pubDate>Thu, 12 Nov 2026 08:00:00 GMT</pubDate><source url="https://reuters.com">Reuters</source>
<description>&lt;a&gt;Nokia wins 5G deal with Operator&lt;/a&gt;</description></item>
<item><title>Nokia wins 5G deal with operator - Yahoo Finance</title><link>https://b</link>
<pubDate>Thu, 12 Nov 2026 07:00:00 GMT</pubDate></item>
<item><title>Old Nokia story - Blog</title><link>https://c</link>
<pubDate>Mon, 02 Nov 2026 07:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_google_news_parse_dedupe_and_window():
    items = news.parse_google_news("NOKIA.HE", feedparser.parse(RSS))
    assert len(items) == 3
    assert items[0].source == "Reuters"
    assert items[0].summary is None  # summary repeating the headline is dropped
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    recent = news.select_recent(items, now, lookback_hours=24, limit=10)
    # same headline from two publishers counts once; the 10-day-old story is dropped
    assert [i.url for i in recent] == ["https://a"]


def test_yahoo_both_formats():
    raw = [
        {"content": {"title": "SAP beats", "pubDate": "2026-11-12T06:00:00Z",
                     "provider": {"displayName": "Reuters"},
                     "canonicalUrl": {"url": "https://s"}, "summary": "<p>Cloud up</p>"}},
        {"title": "SAP guidance", "publisher": "MT", "link": "https://g",
         "providerPublishTime": 1762927200},
        {"content": {}},
    ]
    items = news.parse_yahoo_news("SAP.DE", raw)
    assert [i.title for i in items] == ["SAP beats", "SAP guidance"]
    assert items[0].summary == "Cloud up"
    assert items[0].published_at == datetime(2026, 11, 12, 6, tzinfo=UTC)


def test_store_counts_only_new(conn):
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    it = news.NewsItem("AAPL", "Apple news", "X", "u", None, now)
    assert news.store(conn, [it], now) == 1
    assert news.store(conn, [it], now) == 0


# -------------------------------------------------------------- sessions
def test_entry_and_exit_sessions(cfg):
    us = cfg.market_for("AAPL")
    he = cfg.market_for("NOKIA.HE")
    sessions = [date(2026, 11, d) for d in (9, 10, 11, 12, 13, 16, 17)]
    # 13:00 UTC = 08:00 New York: before the open -> same day
    assert prices.entry_session(datetime(2026, 11, 12, 13, tzinfo=UTC), us, sessions) == date(2026, 11, 12)
    # 15:00 UTC = 10:00 New York: session running -> next day
    assert prices.entry_session(datetime(2026, 11, 12, 15, tzinfo=UTC), us, sessions) == date(2026, 11, 13)
    # 07:30 UTC = 09:30 Helsinki: before the 10:00 open -> same day
    assert prices.entry_session(datetime(2026, 11, 12, 7, 30, tzinfo=UTC), he, sessions) == date(2026, 11, 12)
    # Friday evening -> Monday
    assert prices.entry_session(datetime(2026, 11, 13, 22, tzinfo=UTC), us, sessions) == date(2026, 11, 16)
    assert prices.exit_session(date(2026, 11, 12), 1, sessions) == date(2026, 11, 12)
    assert prices.exit_session(date(2026, 11, 12), 3, sessions) == date(2026, 11, 16)
    assert prices.exit_session(date(2026, 11, 16), 5, sessions) is None


# --------------------------------------------------------------- scoring
def test_costs():
    us = {"commission_pct": 0.05, "commission_min_eur": 1.0, "spread_bps": 10, "fx_bps": 10}
    assert scoring.round_trip_cost(us, 2000) == pytest.approx(0.003)
    eu = {"commission_pct": 0.05, "commission_min_eur": 3.0, "spread_bps": 10, "fx_bps": 0}
    assert scoring.round_trip_cost(eu, 2000) == pytest.approx(0.004)  # minimum fee bites
    assert scoring.borrow_cost(0.5, date(2026, 1, 1), date(2026, 1, 5)) == pytest.approx(0.005 * 5 / 365)


def test_outcome_long_and_short():
    o = scoring.outcome("long", 100, 103, 50, 50.5, 0.003)
    assert o.gross_return == pytest.approx(0.03)
    assert o.net_return == pytest.approx(0.027)
    assert o.net_excess == pytest.approx(0.03 - 0.01 - 0.003)
    s = scoring.outcome("short", 100, 103, 50, 50.5, 0.003)
    assert s.net_return == pytest.approx(-0.033)
    assert s.net_excess == pytest.approx(-(0.03 - 0.01) - 0.003)


def fake_bars(table):
    def bars(symbol, start, end):
        df = table[symbol]
        return df[(df.index >= start) & (df.index <= end)]
    return bars


def frame(rows):
    return pd.DataFrame(rows, columns=["d", "Open", "Close"]).set_index("d")


def test_score_pending_end_to_end(cfg, conn):
    d = lambda x: date(2026, 11, x)
    table = {
        "AAPL": frame([(d(11), 99, 100), (d(12), 100, 101), (d(13), 101, 104), (d(16), 104, 105)]),
        "SPY": frame([(d(11), 50, 50), (d(12), 50, 50.2), (d(13), 50.2, 50.5), (d(16), 50.5, 50.6)]),
    }
    created = datetime(2026, 11, 11, 22, tzinfo=UTC)  # after the close -> enters 12th open
    conn.execute("INSERT INTO signals (analyst, symbol, created_at, direction, horizon_days, confidence)"
                 " VALUES ('claude', 'AAPL', ?, 'long', 2, 4)", (created.isoformat(),))
    # On the 13th during the session, the exit session is not complete yet.
    c = scoring.score_pending(cfg, conn, datetime(2026, 11, 13, 18, tzinfo=UTC), fake_bars(table))
    assert c == {"scored": 0, "waiting": 1, "error": 0}
    c = scoring.score_pending(cfg, conn, datetime(2026, 11, 16, 12, tzinfo=UTC), fake_bars(table))
    assert c["scored"] == 1
    r = conn.execute("SELECT * FROM signals").fetchone()
    assert (r["entry_date"], r["exit_date"]) == ("2026-11-12", "2026-11-13")
    assert r["entry_price"] == 100 and r["exit_price"] == 104
    assert r["bench_return"] == pytest.approx(50.5 / 50 - 1)
    assert r["net_return"] == pytest.approx(0.04 - 0.003)


# --------------------------------------------------------------- analyst
class FakeClient:
    def __init__(self, payload):
        self.payload, self.calls = payload, []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(stop_reason="end_turn", model=kw["model"],
                               content=[SimpleNamespace(type="text", text=json.dumps(self.payload))])


CALL = {"summary": "Big contract", "direction": "long", "horizon_days": 3,
        "confidence": 4, "rationale": "Material", "invalidation": "Deal cancelled"}


def test_parse_call_rejects_bad_values():
    assert analyst.parse_call(json.dumps(CALL), "m").direction == "long"
    with pytest.raises(analyst.AnalystError):
        analyst.parse_call(json.dumps({**CALL, "confidence": 9}), "m")
    with pytest.raises(analyst.AnalystError):
        analyst.parse_call("not json", "m")


def test_analyse_logs_call_and_marks_news(cfg, conn, monkeypatch):
    monkeypatch.setattr(prices, "price_context", lambda *a: "Last close 10.")
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    news.store(conn, [news.NewsItem("NOKIA.HE", "Nokia wins deal", "R", "u", None,
                                    now - timedelta(hours=2))], now)
    client = FakeClient(CALL)
    claude = analyst.ClaudeAnalyst({"name": "claude", "model": "claude-opus-5-5"}, client)
    answered = now + timedelta(seconds=40)
    res = analyst.analyse(cfg, conn, now, analysts=[claude], stocks=[cfg.stock("NOKIA.HE")],
                          clock=lambda: answered)
    assert res[0][2].direction == "long"
    kw = client.calls[0]
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["fallbacks"] == "default"
    assert "Nokia wins deal" in kw["messages"][0]["content"]
    sig = conn.execute("SELECT * FROM signals").fetchone()
    assert sig["created_at"] == answered.isoformat() and sig["status"] == "pending"
    assert sig["analyst"] == "claude"
    # nothing new -> no second call
    analyst.analyse(cfg, conn, now, analysts=[claude], stocks=[cfg.stock("NOKIA.HE")])
    assert len(client.calls) == 1


def test_haiku_gets_no_fallback_param():
    client = FakeClient(CALL)
    analyst.ClaudeAnalyst({"name": "c", "model": "claude-haiku-5-5"}, client).ask("x")
    assert "fallbacks" not in client.calls[0]


class FakeResp:
    def __init__(self, status, payload):
        self.status_code, self._p, self.text = status, payload, json.dumps(payload)

    def json(self):
        return self._p


def test_ollama_request_and_parse():
    sent = []

    def post(url, json, timeout):
        sent.append((url, json))
        return FakeResp(200, {"message": {"role": "assistant", "content": __import__("json").dumps(CALL)}})

    a = analyst.OllamaAnalyst({"name": "local", "model": "qwen3:8b", "think": False}, post=post)
    call = a.ask("prompt")
    assert call.direction == "long" and call.model == "qwen3:8b"
    url, body = sent[0]
    assert url == "http://localhost:11434/api/chat"
    assert body["format"] == analyst.SCHEMA and body["stream"] is False
    assert body["think"] is False and body["options"]["temperature"] == 0


def test_ollama_missing_model_is_fatal():
    a = analyst.OllamaAnalyst({"name": "local", "model": "nope"},
                              post=lambda *a, **k: FakeResp(404, {"error": "not found"}))
    with pytest.raises(analyst.AnalystError) as e:
        a.ask("x")
    assert e.value.fatal and "ollama pull nope" in str(e.value)


def test_two_analysts_same_news_and_fatal_skip(cfg, conn, monkeypatch):
    monkeypatch.setattr(prices, "price_context", lambda *a: None)
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    for sym in ("AAPL", "MSFT"):
        news.store(conn, [news.NewsItem(sym, f"{sym} news", None, None, None, now)], now)
    claude = analyst.ClaudeAnalyst({"name": "claude", "model": "claude-haiku-5-5"}, FakeClient(CALL))
    calls = []

    def down(*a, **k):
        import requests
        calls.append(1)
        raise requests.ConnectionError("refused")

    local = analyst.OllamaAnalyst({"name": "local", "model": "qwen3:8b"}, post=down)
    res = analyst.analyse(cfg, conn, now, analysts=[claude, local],
                          stocks=[cfg.stock("AAPL"), cfg.stock("MSFT")])
    assert len(calls) == 1  # local disabled after the first failure
    assert [r[0] for r in res if not isinstance(r[2], str)] == ["claude", "claude"]
    # local never saw the news, so it is still pending for it on the next run
    assert len(analyst.pending_news(conn, "AAPL", "local", now - timedelta(days=1))) == 1
    assert len(analyst.pending_news(conn, "AAPL", "claude", now - timedelta(days=1))) == 0


def test_none_call_is_not_scored(cfg, conn, monkeypatch):
    monkeypatch.setattr(prices, "price_context", lambda *a: None)
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    news.store(conn, [news.NewsItem("SAP.DE", "SAP listicle", None, None, None, now)], now)
    a = analyst.ClaudeAnalyst({"name": "claude", "model": "claude-haiku-5-5"},
                              FakeClient({**CALL, "direction": "none"}))
    analyst.analyse(cfg, conn, now, analysts=[a], stocks=[cfg.stock("SAP.DE")])
    assert conn.execute("SELECT status FROM signals").fetchone()[0] == "skipped"


# ---------------------------------------------------------------- report
def test_binomial():
    assert report.binom_p_greater(5, 10) == pytest.approx(0.623, abs=1e-3)
    assert report.binom_p_greater(0, 10) == pytest.approx(1.0)


def _insert_scored(conn, n, net, bench, direction="long", conf=4, analyst_name="claude"):
    for i in range(n):
        noise = 0.001 * ((i % 5) - 2)
        conn.execute(
            "INSERT INTO signals (analyst, model, symbol, created_at, direction, horizon_days, confidence,"
            " status, stock_return, bench_return, gross_return, cost, net_return, net_excess)"
            " VALUES (?, 'm', 'AAPL', '2026-11-01T10:00:00+00:00', ?, 2, ?, 'scored', ?, ?, ?, 0.003, ?, ?)",
            (analyst_name, direction, conf, net + noise + 0.003, bench, net + noise + 0.003, net + noise,
             net + noise - bench))


def test_scorecard_gate(cfg, conn):
    now = datetime(2026, 11, 12, tzinfo=UTC)
    assert "No calls logged" in report.scorecard(cfg, conn, now)
    _insert_scored(conn, 50, 0.01, 0.002)
    assert "Not decided yet" in report.scorecard(cfg, conn, now)
    _insert_scored(conn, 400, 0.01, 0.002)
    text = report.scorecard(cfg, conn, now)
    assert "Passed" in text and "Baseline" in text


def test_scorecard_gate_fails(cfg, conn):
    _insert_scored(conn, 450, -0.001, 0.002)
    _insert_scored(conn, 450, 0.01, 0.002, analyst_name="local")
    text = report.scorecard(cfg, conn, datetime(2026, 11, 12, tzinfo=UTC))
    assert "| claude | **Failed** |" in text and "| local | **Passed** |" in text


def test_brief(conn):
    now = datetime(2026, 11, 12, 12, tzinfo=UTC)
    for a, d in (("claude", "short"), ("local", "long")):
        conn.execute("INSERT INTO signals (analyst, symbol, created_at, direction, horizon_days,"
                     " confidence, summary, rationale, invalidation)"
                     " VALUES (?, 'AAPL', ?, ?, 2, 3, 'S', 'R', 'I')", (a, now.isoformat(), d))
    text = report.brief(conn, now)
    assert "claude: SHORT, confidence 3/5" in text and "local: LONG" in text
    assert "disagree" in text
