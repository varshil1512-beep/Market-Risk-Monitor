from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from alphapulse.config import load_portfolio_config
from alphapulse.data_pipeline import fetch_market_data, run_pipeline


def fetch_only() -> tuple:
    """Fetch raw market data for the configured portfolio."""
    config = load_portfolio_config()
    return fetch_market_data(config)


def process_data() -> dict:
    """Run the full data acquisition and processing pipeline."""
    config = load_portfolio_config()
    return run_pipeline(config)


if __name__ == "__main__":
    results = process_data()
    print(results)
