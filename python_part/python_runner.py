from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from alphapulse.config import load_portfolio_config
from alphapulse.data_pipeline import run_pipeline


def run_python_analysis() -> dict:
    """Run the quantitative finance analysis layer."""
    config = load_portfolio_config()
    return run_pipeline(config)


if __name__ == "__main__":
    print(json.dumps(run_python_analysis(), indent=2))
