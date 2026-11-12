"""Ask one or more AI analysts for a view on a stock's fresh headlines and log
each call. Every analyst sees the same news and is scored the same way, so the
scorecard can compare them."""
from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .config import Config, Stock
from . import prices

log = logging.getLogger(__name__)

# Claude models that accept the server-side refusal fallback.
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
sentences each. Answer with the JSON object only."""

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
    """`fatal` means the analyst cannot work at all this run (server down,
    model missing, bad key), so the remaining stocks skip it."""

    def __init__(self, msg: str, fatal: bool = False):
        super().__init__(msg)
        self.fatal = fatal


def parse_call(text: str, model: str) -> Call:
    try:
        d = json.loads(text)
    except json.JSONDecodeError as e:
        raise AnalystError(f"Invalid JSON: {e}") from e
    if not isinstance(d, dict):
        raise AnalystError("Answer is not a JSON object")
    if d.get("direction") not in ("long", "short", "none"):
        raise AnalystError(f"Bad direction {d.get('direction')!r}")
    if d.get("horizon_days") not in range(1, 6) or d.get("confidence") not in range(1, 6):
        raise AnalystError("Horizon or confidence out of range")
    for k in ("summary", "rationale", "invalidation"):
        if not isinstance(d.get(k), str):
            raise AnalystError(f"Missing {k}")
    return Call(d["direction"], d["horizon_days"], d["confidence"], d["summary"],
                d["rationale"], d["invalidation"], model)


# ------------------------------------------------------------------ analysts
class ClaudeAnalyst:
    def __init__(self, spec: dict, client=None):
        self.name = spec["name"]
        self.model = spec["model"]
        self.effort = spec.get("effort", "medium")
        self.max_tokens = spec.get("max_tokens", 16000)
        self._client = client

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def ask(self, prompt: str) -> Call:
        import anthropic

        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": self.effort,
                           "format": {"type": "json_schema", "schema": SCHEMA}},
        )
        if self.model in FALLBACK_MODELS:
            kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        try:
            resp = self.client.beta.messages.create(**kwargs)
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError,
                anthropic.NotFoundError) as e:
            raise AnalystError(f"API error {e.status_code}: {e.message}", fatal=True) from e
        except anthropic.APIStatusError as e:
            raise AnalystError(f"API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise AnalystError(f"Network error: {e}") from e
        except anthropic.AnthropicError as e:  # e.g. no API key configured
            raise AnalystError(str(e), fatal=True) from e

        if resp.stop_reason == "refusal":
            raise AnalystError("Model declined the request")
        if resp.stop_reason == "max_tokens":
            raise AnalystError("Response cut off at max_tokens")
        text = next((b.text for b in resp.content if b.type == "text"), None)
        if text is None:
            raise AnalystError("No text in response")
        return parse_call(text, resp.model)


class OllamaAnalyst:
    """A model running on this computer through Ollama (ollama.com)."""

    def __init__(self, spec: dict, post=None):
        self.name = spec["name"]
        self.model = spec["model"]
        self.host = spec.get("host", "http://localhost:11434").rstrip("/")
        self.think = spec.get("think")          # None = model default
        self.timeout = spec.get("timeout_s", 600)
        self.options = {"temperature": 0, "num_ctx": 8192, **spec.get("options", {})}
        self._post = post

    def ask(self, prompt: str) -> Call:
        import requests

        post = self._post or requests.post
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt}],
            "format": SCHEMA,
            "stream": False,
            "options": self.options,
        }
        if self.think is not None:
            body["think"] = self.think
        try:
            r = post(f"{self.host}/api/chat", json=body, timeout=self.timeout)
        except requests.ConnectionError as e:
            raise AnalystError(f"Ollama not reachable at {self.host}. Is it running?",
                               fatal=True) from e
        except requests.Timeout as e:
            raise AnalystError(f"Ollama took longer than {self.timeout}s") from e
        if r.status_code == 404:
            raise AnalystError(f"Model {self.model} not installed. Run: ollama pull {self.model}",
                               fatal=True)
        if r.status_code != 200:
            raise AnalystError(f"Ollama error {r.status_code}: {r.text[:200]}")
        content = (r.json().get("message") or {}).get("content", "")
        return parse_call(content, self.model)


PROVIDERS = {"anthropic": ClaudeAnalyst, "ollama": OllamaAnalyst}


def make_analysts(cfg: Config, only: list[str] | None = None) -> list:
    out = []
    for spec in cfg.analysts:
        if spec.get("enabled", True) and (not only or spec["name"] in only):
            out.append(PROVIDERS[spec["provider"]](spec))
    return out


# ---------------------------------------------------------------- the run
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


def pending_news(conn: sqlite3.Connection, symbol: str, analyst: str,
                 cutoff: datetime) -> list:
    """Headlines in the window that this analyst has not seen yet."""
    return conn.execute(
        "SELECT * FROM news n WHERE symbol=? AND published_at >= ? AND NOT EXISTS"
        " (SELECT 1 FROM news_seen s WHERE s.news_id=n.id AND s.analyst=?)"
        " ORDER BY published_at DESC", (symbol, cutoff.isoformat(), analyst),
    ).fetchall()


def analyse(cfg: Config, conn: sqlite3.Connection, now: datetime,
            analysts: list | None = None, stocks: list[Stock] | None = None,
            clock=None) -> list[tuple[str, str, Call | str]]:
    """Run every analyst over every stock with unread news.
    Returns (analyst name, symbol, Call or error message).

    Each call is timestamped when its answer arrives (`clock`), not when the
    run started, so it is never credited with a price it could not have used."""
    clock = clock or (lambda: datetime.now(timezone.utc))
    analysts = make_analysts(cfg) if analysts is None else analysts
    cutoff = now - timedelta(hours=cfg.news["lookback_hours"])
    disabled: set[str] = set()
    results = []
    for stock in stocks or cfg.stocks:
        market = cfg.market_for(stock.symbol)
        context = None
        for a in analysts:
            if a.name in disabled:
                continue
            rows = pending_news(conn, stock.symbol, a.name, cutoff)
            if not rows:
                continue
            rows = rows[: cfg.news["max_items_per_ticker"]]
            if context is None:
                context = prices.price_context(stock.symbol, now.date()) or ""
            earlier = conn.execute(
                "SELECT * FROM signals WHERE symbol=? AND analyst=? AND created_at >= ?"
                " ORDER BY created_at",
                (stock.symbol, a.name, (now - timedelta(days=5)).isoformat()),
            ).fetchall()
            prompt = build_prompt(stock, market.region, now, rows, context, earlier)
            try:
                call = a.ask(prompt)
            except AnalystError as e:
                log.warning("%s / %s: %s", a.name, stock.symbol, e)
                results.append((a.name, stock.symbol, str(e)))
                if e.fatal:
                    disabled.add(a.name)
                continue
            created = clock().isoformat()
            ids = [r["id"] for r in rows]
            conn.execute(
                "INSERT INTO signals (analyst, symbol, created_at, direction, horizon_days,"
                " confidence, summary, rationale, invalidation, news_ids, model, status)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (a.name, stock.symbol, created, call.direction, call.horizon_days,
                 call.confidence, call.summary, call.rationale, call.invalidation,
                 json.dumps(ids), call.model,
                 "pending" if call.direction != "none" else "skipped"),
            )
            conn.executemany(
                "INSERT OR IGNORE INTO news_seen (news_id, analyst, seen_at) VALUES (?,?,?)",
                [(i, a.name, created) for i in ids])
            conn.commit()
            results.append((a.name, stock.symbol, call))
    return results
