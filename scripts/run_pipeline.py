from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from alphapulse.config import load_portfolio_config
from alphapulse.data_pipeline import run_pipeline


def main() -> None:
    config = load_portfolio_config()
    results = run_pipeline(config)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
