"""Load config.yaml and watchlist.yaml."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Market:
    suffix: str
    region: str
    tz: str
    open: str  # "HH:MM" local exchange time
    benchmark: str


@dataclass(frozen=True)
class Stock:
    symbol: str
    name: str
    query: str | None = None

    @property
    def suffix(self) -> str:
        return "." + self.symbol.rsplit(".", 1)[1] if "." in self.symbol else ""

    @property
    def search_query(self) -> str:
        return self.query or f'"{self.name}" stock'


@dataclass
class Config:
    root: Path
    database: Path
    analysts: list[dict]
    news: dict
    scoring: dict
    report: dict
    markets: dict[str, Market]
    stocks: list[Stock] = field(default_factory=list)

    def market_for(self, symbol: str) -> Market:
        suffix = "." + symbol.rsplit(".", 1)[1] if "." in symbol else ""
        if suffix not in self.markets:
            raise KeyError(f"No market configured for suffix {suffix!r} ({symbol})")
        return self.markets[suffix]

    def stock(self, symbol: str) -> Stock:
        for s in self.stocks:
            if s.symbol == symbol:
                return s
        raise KeyError(symbol)


def load(config_path: Path | None = None, watchlist_path: Path | None = None) -> Config:
    config_path = Path(config_path or ROOT / "config.yaml")
    watchlist_path = Path(watchlist_path or config_path.parent / "watchlist.yaml")
    raw = yaml.safe_load(config_path.read_text())
    wl = yaml.safe_load(watchlist_path.read_text())
    markets = {
        suffix: Market(suffix=suffix, **m) for suffix, m in raw["markets"].items()
    }
    stocks = [Stock(**s) for s in wl["stocks"]]
    cfg = Config(
        root=config_path.parent,
        database=config_path.parent / raw["database"],
        analysts=raw["analysts"],
        news=raw["news"],
        scoring=raw["scoring"],
        report=raw["report"],
        markets=markets,
        stocks=stocks,
    )
    for s in stocks:  # fail early on a symbol with no market
        cfg.market_for(s.symbol)
    names = [a["name"] for a in cfg.analysts]
    if len(set(names)) != len(names):
        raise ValueError("Analyst names in config.yaml must be unique")
    for a in cfg.analysts:
        if a.get("provider") not in ("anthropic", "ollama"):
            raise ValueError(f"Analyst {a['name']}: provider must be anthropic or ollama")
    return cfg
