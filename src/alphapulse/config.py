from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = ROOT_DIR / "outputs"


@dataclass(frozen=True)
class Holding:
    ticker: str
    name: str
    sector: str
    weight: float


@dataclass(frozen=True)
class PortfolioConfig:
    portfolio_name: str
    benchmark: str
    lookback_years: int
    trading_days: int
    risk_confidence_level: float
    monte_carlo_runs: int
    forecast_horizon_days: int
    portfolio_value_usd: float
    holdings: list[Holding]

    @property
    def tickers(self) -> list[str]:
        return [holding.ticker for holding in self.holdings]

    @property
    def weights(self) -> list[float]:
        return [holding.weight for holding in self.holdings]


def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_portfolio_config(path: Path | None = None) -> PortfolioConfig:
    config_path = path or (CONFIG_DIR / "portfolio.json")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    holdings = [Holding(**holding) for holding in payload["holdings"]]
    weight_total = round(sum(holding.weight for holding in holdings), 10)
    if weight_total != 1.0:
        raise ValueError(f"Portfolio weights must sum to 1.0, found {weight_total}")
    return PortfolioConfig(
        portfolio_name=payload["portfolio_name"],
        benchmark=payload["benchmark"],
        lookback_years=payload["lookback_years"],
        trading_days=payload["trading_days"],
        risk_confidence_level=payload["risk_confidence_level"],
        monte_carlo_runs=payload["monte_carlo_runs"],
        forecast_horizon_days=payload["forecast_horizon_days"],
        portfolio_value_usd=payload["portfolio_value_usd"],
        holdings=holdings,
    )
