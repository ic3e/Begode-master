"""Command line: python -m newsdesk <command>."""
from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from . import analyst, config, db, news, report, scoring


def _write(text: str, out: str | None) -> None:
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text)
        print(f"Wrote {out}")
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="newsdesk", description=__doc__)
    p.add_argument("--config", help="path to config.yaml")
    p.add_argument("--only", help="comma-separated symbols to limit the run to")
    p.add_argument("--analyst", help="comma-separated analyst names to run (default: all enabled)")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="collect news only, no AI")
    sub.add_parser("analyse", help="send unread news to the AI and log calls")
    sub.add_parser("run", help="fetch + analyse + score (the scheduled job)")
    sub.add_parser("score", help="score calls whose exit session has closed")
    r = sub.add_parser("report", help="scorecard with the Gate 1 check")
    r.add_argument("--out")
    b = sub.add_parser("brief", help="latest calls in readable form")
    b.add_argument("--hours", type=float, default=24)
    b.add_argument("--out")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")
    cfg = config.load(args.config)
    stocks = None
    if args.only:
        stocks = [cfg.stock(s.strip()) for s in args.only.split(",")]
    conn = db.connect(cfg.database)
    now = datetime.now(timezone.utc)

    if args.cmd in ("fetch", "run"):
        counts = news.collect(cfg, conn, now, stocks)
        print(f"News: {sum(counts.values())} new headlines across "
              f"{sum(1 for c in counts.values() if c)} stocks.")
    if args.cmd in ("analyse", "run"):
        only = args.analyst.split(",") if args.analyst else None
        team = analyst.make_analysts(cfg, only)
        results = analyst.analyse(cfg, conn, now, analysts=team, stocks=stocks)
        for a in team:
            mine = [c for n, _, c in results if n == a.name]
            calls = [c for c in mine if isinstance(c, analyst.Call)]
            errors = [c for c in mine if isinstance(c, str)]
            active = [c for c in calls if c.direction != "none"]
            print(f"{a.name} ({a.model}): {len(calls)} stocks reviewed, {len(active)} calls "
                  f"({sum(c.direction == 'long' for c in active)} long, "
                  f"{sum(c.direction == 'short' for c in active)} short), {len(errors)} errors.")
            for e in dict.fromkeys(errors):
                print(f"  error: {e}")
    if args.cmd in ("score", "run"):
        c = scoring.score_pending(cfg, conn, now)
        print(f"Scoring: {c['scored']} scored, {c['waiting']} waiting, {c['error']} failed.")
    if args.cmd == "report":
        _write(report.scorecard(cfg, conn, now), args.out)
    if args.cmd == "brief":
        _write(report.brief(conn, now, args.hours), args.out)
    return 0
