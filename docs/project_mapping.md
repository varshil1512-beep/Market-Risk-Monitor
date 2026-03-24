# Market-Risk-monitor Project Mapping

This project is built directly against **Project 2: Finance - Market Volatility & Portfolio Risk Dashboard** from the internship PDF.

## Requirement Coverage

**Use case**

- Boutique investment firm portfolio risk monitoring
- Diversification support through stock correlation analysis
- Portfolio downside estimation through Value at Risk

**Basic core metrics**

- Stock price line charts
- Trading volume bars
- Daily percentage returns

**Deep analytics**

- Monte Carlo simulation with **10,000 runs**
- Dynamic stock correlation heatmap
- Rolling **30-day** volatility
- Historical portfolio VaR and CVaR
- Max drawdown

**Implementation details from PDF**

- Python-based pipeline
- `yfinance` for market data retrieval
- NumPy matrix operations for portfolio risk calculations
- Tableau-ready outputs generated to CSV

## Week-by-Week Alignment

### Week 1: Data Acquisition & Cleaning

- 10 diversified stocks selected across multiple sectors
- S&P 500 benchmark included
- Historical adjusted prices and volume collected through `yfinance`
- Corporate-action-safe adjusted close used to reflect split/dividend adjustments

### Week 2: Quantitative Analysis

- Daily log returns computed with NumPy/Pandas
- Portfolio returns calculated with configurable weights
- Monte Carlo simulation implemented for a 1-year horizon
- Distribution statistics exported for validation

### Week 3: Visual Storytelling

- Interactive dashboard created locally
- What-if sector shock control included
- Tableau-ready processed datasets exported

### Week 4: Finalization

- Executive summary output generated
- Refresh process consolidated into one command: `python scripts/run_pipeline.py`
- Dashboard ready for internship submission/demo
