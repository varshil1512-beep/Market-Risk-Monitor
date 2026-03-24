# Tableau Build Guide

Use the exported files in `data/processed/` to recreate the BI layer in Tableau exactly around the internship brief.

## Recommended Tableau Data Sources

- `prices_long.csv`
- `volumes_long.csv`
- `returns_long.csv`
- `rolling_volatility.csv`
- `correlation_matrix_long.csv`
- `portfolio_kpis.csv`
- `monte_carlo_percentiles.csv`
- `drawdown.csv`

## Dashboard Layout

### Sheet 1: Executive Summary

- KPI cards:
  - Daily VaR (USD)
  - Daily CVaR (USD)
  - Annualized Volatility
  - Max Drawdown
  - Expected Terminal Value
  - Probability of Loss

### Sheet 2: Market Performance

- Line chart using `prices_long.csv`
- Volume bar chart using `volumes_long.csv`
- Daily returns line chart using `returns_long.csv`

### Sheet 3: Risk Diagnostics

- Heatmap from `correlation_matrix_long.csv`
- Rolling volatility trend from `rolling_volatility.csv`
- Drawdown area chart from `drawdown.csv`

### Sheet 4: Monte Carlo Forecast

- Percentile bands from `monte_carlo_percentiles.csv`
- Median path emphasized

### Parameter Suggestion

Create a Tableau parameter called `Sector Shock %` and a parameter for `Target Sector`. Use calculated fields to simulate sector-specific return shocks during dashboard interaction.
