"""Ask Claude for a view on one stock's fresh headlines and log the call."""
from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .config import Config, Stock
from . import prices

log = logging.getLogger(__name__)

# Models that accept the server-side refusal fallback.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5",
                   "claude-fable-5-2", "claude-fable-5-1"}

SYSTEM = """\
You review fresh news about one listed company for a research log. Each call \
you make is timestamped, then scored automatically: as if bought (long) or sold \
short (short) at the open of the next trading session after your call, and \
closed after the number of sessions you choose (1 to 5), net of trading costs \
of roughly 0.3%, and compared with the stock market index over the same days.

What that means for your judgement:
- The first price reaction to a headline happens within seconds to minutes. \
By the next open it is already in the price. Only call a direction when the \
news is likely to keep moving the stock relative to the market after that: \
for example an earnings surprise with guidance change, a material contract, \
a regulatory decision, an analyst-consensus shift, or a slow-burning problem \
the market may still be digesting.
- Most headlines do not qualify: rehashes, opinion and listicle pieces, \
"stock X is up today" reports, market-wide moves, and old news resurfacing. \
For these, answer "none". "none" is the expected answer most of the time.
- Use the recent price change if given: a stock that already moved a lot on \
the news may have priced it in.
- Rely only on the headlines and summaries provided. Do not assume facts that \
are not in them. If the headlines conflict or are vague, lower your confidence \
or answer "none".
- Confidence is 1 (barely better than a coin flip) to 5 (rare: clear, \
material and under-reacted news). Reserve 4 and 5 for genuinely strong cases.
- "long" means you expect the stock to beat the index; "short" means you \
expect it to trail the index.

Write the summary, rationale and invalidation in plain English, one or two \
sentences each."""

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string",
                    "description": "What happened, from the headlines."},
        "direction": {"type": "string", "enum": ["long", "short", "none"]},
        "horizon_days": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
        "confidence": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
        "rationale": {"type": "string",
                      "description": "Why the price may keep moving, or why not."},
        "invalidation": {"type": "string",
                         "description": "What would show the call is wrong."},
    },
    "required": ["summary", "direction", "horizon_days", "confidence",
                 "rationale", "invalidation"],
    "additionalProperties": False,
}


@dataclass
class Call:
    direction: str
    horizon_days: int
    confidence: int
    summary: str
    rationale: str
    invalidation: str
    model: str


class AnalystError(RuntimeError):
    pass


def build_prompt(stock: Stock, region: str, now: datetime, news_rows: list,
                 context: str | None, earlier: list) -> str:
    lines = [
        f"Company: {stock.name} ({stock.symbol}), {region} listing.",
        f"Time of this review: {now:%Y-%m-%d %H:%M} UTC.",
    ]
    if context:
        lines.append(f"Recent price action: {context}")
    if earlier:
        lines.append("\nYour earlier calls on this stock in the last 5 days:")
        for s in earlier:
            lines.append(f"- {s['created_at'][:16]} UTC: {s['direction']}, "
                         f"confidence {s['confidence']}, {s['horizon_days']} sessions. "
                         f"{s['summary']}")
    lines.append("\nNew headlines (newest first):")
    for i, n in enumerate(news_rows, 1):
        when = (n["published_at"] or "")[:16].replace("T", " ")
        src = f" ({n['source']})" if n["source"] else ""
        lines.append(f"{i}. [{when} UTC]{src} {n['title']}")
        if n["summary"]:
            lines.append(f"   {n['summary']}")
    lines.append("\nGive your call.")
    return "\n".join(lines)


def ask(client, cfg: Config, prompt: str) -> Call:
    import anthropic

    model = cfg.ai["model"]
    kwargs = dict(
        model=model,
        max_tokens=cfg.ai.get("max_tokens", 16000),
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": cfg.ai.get("effort", "medium"),
                       "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if model in FALLBACK_MODELS:
        kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    try:
        resp = client.beta.messages.create(**kwargs)
    except anthropic.APIStatusError as e:
        raise AnalystError(f"API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise AnalystError(f"Network error: {e}") from e

    if resp.stop_reason == "refusal":
        raise AnalystError("Model declined the request")
    if resp.stop_reason == "max_tokens":
        raise AnalystError("Response cut off at max_tokens")
    text = next((b.text for b in resp.content if b.type == "text"), None)
    if text is None:
        raise AnalystError("No text in response")
    return parse_call(text, resp.model)


def parse_call(text: str, model: str) -> Call:
    try:
        d = json.loads(text)
    except json.JSONDecodeError as e:
        raise AnalystError(f"Invalid JSON: {e}") from e
    if d.get("direction") not in ("long", "short", "none"):
        raise AnalystError(f"Bad direction {d.get('direction')!r}")
    if d.get("horizon_days") not in range(1, 6) or d.get("confidence") not in range(1, 6):
        raise AnalystError("Horizon or confidence out of range")
    return Call(d["direction"], d["horizon_days"], d["confidence"], d["summary"],
                d["rationale"], d["invalidation"], model)


def pending_news(conn: sqlite3.Connection, symbol: str, cutoff: datetime) -> list:
    return conn.execute(
        "SELECT * FROM news WHERE symbol=? AND analysed_at IS NULL AND published_at >= ?"
        " ORDER BY published_at DESC", (symbol, cutoff.isoformat()),
    ).fetchall()


def analyse(cfg: Config, conn: sqlite3.Connection, now: datetime, client=None,
            stocks: list[Stock] | None = None,
            clock=None) -> list[tuple[str, Call | str]]:
    """Analyse every stock with unread news. Returns (symbol, Call or error).

    Each call is timestamped when the answer arrives (`clock`), not when the
    run started, so it is never credited with a price it could not have used."""
    clock = clock or (lambda: datetime.now(timezone.utc))
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    cutoff = now - timedelta(hours=cfg.news["lookback_hours"])
    results = []
    for stock in stocks or cfg.stocks:
        rows = pending_news(conn, stock.symbol, cutoff)
        if not rows:
            continue
        rows = rows[: cfg.news["max_items_per_ticker"]]
        market = cfg.market_for(stock.symbol)
        earlier = conn.execute(
            "SELECT * FROM signals WHERE symbol=? AND created_at >= ? ORDER BY created_at",
            (stock.symbol, (now - timedelta(days=5)).isoformat()),
        ).fetchall()
        prompt = build_prompt(stock, market.region, now, rows,
                              prices.price_context(stock.symbol, now.date()), earlier)
        try:
            call = ask(client, cfg, prompt)
        except AnalystError as e:
            log.warning("%s: %s", stock.symbol, e)
            results.append((stock.symbol, str(e)))
            continue
        ids = [r["id"] for r in rows]
        created = clock()
        conn.execute(
            "INSERT INTO signals (symbol, created_at, direction, horizon_days, confidence,"
            " summary, rationale, invalidation, news_ids, model, status)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (stock.symbol, created.isoformat(), call.direction, call.horizon_days,
             call.confidence, call.summary, call.rationale, call.invalidation,
             json.dumps(ids), call.model,
             "pending" if call.direction != "none" else "skipped"),
        )
        conn.executemany("UPDATE news SET analysed_at=? WHERE id=?",
                         [(created.isoformat(), i) for i in ids])
        conn.commit()
        results.append((stock.symbol, call))
    return results
