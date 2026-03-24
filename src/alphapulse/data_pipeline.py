from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

from alphapulse.analytics import (
    build_price_long_frame,
    build_returns_long_frame,
    compute_correlation_matrix,
    compute_drawdown,
    compute_historical_var,
    compute_log_returns,
    compute_portfolio_returns,
    compute_portfolio_summary,
    compute_rolling_volatility,
    holdings_frame,
    monte_carlo_simulation,
)
from alphapulse.config import OUTPUTS_DIR, PROCESSED_DIR, RAW_DIR, PortfolioConfig, ensure_directories
from alphapulse.io_utils import write_csv, write_json


def fetch_market_data(config: PortfolioConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_directories()
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=365 * config.lookback_years + 30)
    tickers = config.tickers + [config.benchmark]

    dataset = yf.download(
        tickers=tickers,
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        auto_adjust=True,
        actions=True,
        progress=False,
        group_by="column",
        threads=False,
    )
    if dataset.empty:
        raise RuntimeError("No market data returned from yfinance.")

    if isinstance(dataset.columns, pd.MultiIndex):
        close_frame = dataset["Close"].copy()
        volume_frame = dataset["Volume"].copy()
    else:
        close_frame = dataset[["Close"]].rename(columns={"Close": tickers[0]})
        volume_frame = dataset[["Volume"]].rename(columns={"Volume": tickers[0]})

    close_frame.index.name = "Date"
    volume_frame.index.name = "Date"
    close_frame = close_frame.sort_index().ffill().dropna(how="all")
    volume_frame = volume_frame.sort_index().fillna(0)

    close_frame.to_csv(RAW_DIR / "close_prices_wide.csv")
    volume_frame.to_csv(RAW_DIR / "volumes_wide.csv")
    return close_frame, volume_frame


def run_pipeline(config: PortfolioConfig) -> dict:
    prices_wide, volumes_wide = fetch_market_data(config)

    asset_prices = prices_wide[config.tickers].copy()
    asset_returns = compute_log_returns(asset_prices)
    full_returns = compute_log_returns(prices_wide)
    weights = np.array(config.weights)

    portfolio_returns = compute_portfolio_returns(asset_returns, weights)
    rolling_volatility = compute_rolling_volatility(asset_returns, config.trading_days)
    correlation_long = compute_correlation_matrix(asset_returns)
    var_metrics = compute_historical_var(portfolio_returns, config.risk_confidence_level, config.portfolio_value_usd)
    drawdown_df, max_drawdown = compute_drawdown(portfolio_returns)
    monte_carlo_percentiles, monte_carlo_sample_paths, monte_carlo_summary = monte_carlo_simulation(
        returns=asset_returns,
        weights=weights,
        horizon_days=config.forecast_horizon_days,
        runs=config.monte_carlo_runs,
        portfolio_value=config.portfolio_value_usd,
    )

    prices_long = build_price_long_frame(prices_wide, config.holdings, config.benchmark)
    returns_long = build_returns_long_frame(full_returns, config.holdings, config.benchmark)
    volumes_long = volumes_wide.reset_index().melt(id_vars="Date", var_name="ticker", value_name="volume")
    holdings_df = holdings_frame(config.holdings)
    kpis = compute_portfolio_summary(config, portfolio_returns, var_metrics, max_drawdown, monte_carlo_summary)

    portfolio_returns_df = portfolio_returns.reset_index()
    portfolio_returns_df.columns = ["Date", "portfolio_log_return"]
    portfolio_returns_df["portfolio_daily_pct_return"] = np.expm1(portfolio_returns_df["portfolio_log_return"]) * 100

    kpi_df = pd.DataFrame([kpis])

    write_csv(prices_long, PROCESSED_DIR / "prices_long.csv")
    write_csv(prices_wide.reset_index(), PROCESSED_DIR / "prices_wide.csv")
    write_csv(returns_long, PROCESSED_DIR / "returns_long.csv")
    write_csv(volumes_long, PROCESSED_DIR / "volumes_long.csv")
    write_csv(rolling_volatility, PROCESSED_DIR / "rolling_volatility.csv")
    write_csv(correlation_long, PROCESSED_DIR / "correlation_matrix_long.csv")
    write_csv(drawdown_df, PROCESSED_DIR / "drawdown.csv")
    write_csv(portfolio_returns_df, PROCESSED_DIR / "portfolio_returns.csv")
    write_csv(holdings_df, PROCESSED_DIR / "portfolio_holdings.csv")
    write_csv(monte_carlo_percentiles, PROCESSED_DIR / "monte_carlo_percentiles.csv")
    write_csv(monte_carlo_sample_paths, PROCESSED_DIR / "monte_carlo_sample_paths.csv")
    write_csv(kpi_df, PROCESSED_DIR / "portfolio_kpis.csv")
    write_json(kpis, OUTPUTS_DIR / "executive_summary.json")

    return {
        "prices_rows": len(prices_long),
        "returns_rows": len(returns_long),
        "portfolio_observations": len(portfolio_returns_df),
        "kpis": kpis,
    }
