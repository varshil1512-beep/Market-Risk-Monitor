from __future__ import annotations

from dataclasses import asdict

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

from alphapulse.config import Holding, PortfolioConfig


def compute_log_returns(price_frame: pd.DataFrame) -> pd.DataFrame:
    returns = np.log(price_frame / price_frame.shift(1))
    return returns.dropna(how="all")


def compute_portfolio_returns(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    aligned = returns.dropna()
    return pd.Series(aligned.to_numpy() @ weights, index=aligned.index, name="portfolio_log_return")


def compute_rolling_volatility(returns: pd.DataFrame, trading_days: int, window: int = 30) -> pd.DataFrame:
    volatility = returns.rolling(window=window).std() * np.sqrt(trading_days)
    volatility = volatility.reset_index().melt(id_vars="Date", var_name="ticker", value_name="rolling_volatility")
    return volatility.dropna()


def compute_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    correlation = returns.corr()
    correlation.index.name = "ticker"
    return correlation.reset_index().melt(id_vars="ticker", var_name="ticker_compare", value_name="correlation")


def compute_historical_var(portfolio_returns: pd.Series, confidence_level: float, portfolio_value: float) -> dict:
    quantile = np.quantile(portfolio_returns, 1 - confidence_level)
    var_value = abs(quantile) * portfolio_value
    cvar_value = abs(portfolio_returns[portfolio_returns <= quantile].mean()) * portfolio_value
    return {
        "confidence_level": confidence_level,
        "daily_var_pct": float(abs(quantile)),
        "daily_var_usd": float(var_value),
        "daily_cvar_usd": float(cvar_value),
    }


def compute_drawdown(portfolio_returns: pd.Series) -> tuple[pd.DataFrame, float]:
    cumulative = np.exp(portfolio_returns.cumsum())
    rolling_peak = cumulative.cummax()
    drawdown = (cumulative / rolling_peak) - 1
    drawdown_df = pd.DataFrame(
        {
            "Date": portfolio_returns.index,
            "cumulative_growth": cumulative.values,
            "drawdown": drawdown.values,
        }
    )
    return drawdown_df, float(drawdown.min())


def monte_carlo_simulation(
    returns: pd.DataFrame,
    weights: np.ndarray,
    horizon_days: int,
    runs: int,
    portfolio_value: float,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    mean_returns = returns.mean().to_numpy()
    covariance = returns.cov().to_numpy()
    chol = np.linalg.cholesky(covariance)
    random_shocks = np.random.normal(size=(horizon_days, runs, len(weights)))
    correlated_shocks = np.einsum("ij,trj->tri", chol, random_shocks)
    simulated_asset_returns = mean_returns + correlated_shocks
    simulated_portfolio_returns = np.einsum("tri,i->tr", simulated_asset_returns, weights)
    simulated_paths = portfolio_value * np.exp(np.cumsum(simulated_portfolio_returns, axis=0))

    percentile_frame = pd.DataFrame(
        {
            "day": np.arange(1, horizon_days + 1),
            "p05": np.percentile(simulated_paths, 5, axis=1),
            "p50": np.percentile(simulated_paths, 50, axis=1),
            "p95": np.percentile(simulated_paths, 95, axis=1),
            "mean_path": simulated_paths.mean(axis=1),
        }
    )
    sample_paths = pd.DataFrame(simulated_paths[:, :100])
    sample_paths.insert(0, "day", np.arange(1, horizon_days + 1))
    sample_paths.columns = ["day"] + [f"path_{idx:03d}" for idx in range(1, sample_paths.shape[1])]

    terminal_values = simulated_paths[-1, :]
    summary = {
        "forecast_horizon_days": horizon_days,
        "runs": runs,
        "expected_terminal_value": float(np.mean(terminal_values)),
        "median_terminal_value": float(np.median(terminal_values)),
        "worst_case_p05": float(np.percentile(terminal_values, 5)),
        "best_case_p95": float(np.percentile(terminal_values, 95)),
        "return_skewness": float(skew(np.log(terminal_values / portfolio_value))),
        "return_kurtosis": float(kurtosis(np.log(terminal_values / portfolio_value), fisher=True)),
        "probability_of_loss": float(np.mean(terminal_values < portfolio_value)),
    }
    return percentile_frame, sample_paths, summary


def holdings_frame(holdings: list[Holding]) -> pd.DataFrame:
    rows = [asdict(holding) for holding in holdings]
    return pd.DataFrame(rows)


def build_price_long_frame(price_frame: pd.DataFrame, holdings: list[Holding], benchmark: str) -> pd.DataFrame:
    sector_map = {holding.ticker: holding.sector for holding in holdings}
    name_map = {holding.ticker: holding.name for holding in holdings}
    sector_map[benchmark] = "Benchmark"
    name_map[benchmark] = "S&P 500"
    long_df = price_frame.reset_index().melt(id_vars="Date", var_name="ticker", value_name="close")
    long_df["asset_name"] = long_df["ticker"].map(name_map)
    long_df["sector"] = long_df["ticker"].map(sector_map)
    return long_df


def build_returns_long_frame(returns: pd.DataFrame, holdings: list[Holding], benchmark: str) -> pd.DataFrame:
    sector_map = {holding.ticker: holding.sector for holding in holdings}
    sector_map[benchmark] = "Benchmark"
    long_df = returns.reset_index().melt(id_vars="Date", var_name="ticker", value_name="log_return")
    long_df["daily_pct_return"] = np.expm1(long_df["log_return"]) * 100
    long_df["sector"] = long_df["ticker"].map(sector_map)
    return long_df.dropna()


def compute_portfolio_summary(
    config: PortfolioConfig,
    portfolio_returns: pd.Series,
    var_metrics: dict,
    max_drawdown: float,
    monte_carlo_summary: dict,
) -> dict:
    annualized_volatility = float(portfolio_returns.std() * np.sqrt(config.trading_days))
    annualized_return = float(portfolio_returns.mean() * config.trading_days)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility else 0.0
    return {
        "portfolio_name": config.portfolio_name,
        "benchmark": config.benchmark,
        "portfolio_value_usd": config.portfolio_value_usd,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio_proxy": float(sharpe_ratio),
        "max_drawdown": max_drawdown,
        **var_metrics,
        **monte_carlo_summary,
    }
