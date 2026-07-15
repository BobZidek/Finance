# Potential Enhancements

- **Formal Kupiec test**: implement the actual Kupiec Proportion-of-Failures likelihood-ratio
  test (with a p-value) rather than a simple exceedance-count comparison, for a statistically
  rigorous VaR backtest.
- **Conditional coverage (Christoffersen) test**: extend backtesting to check not just the
  exceedance *rate* but whether exceedances cluster together in time (a sign of a model that
  misses volatility regime changes), which the simple exceedance count misses.
- **Multi-day VaR scaling**: extend from 1-day VaR to 10-day (regulatory standard) VaR, and
  discuss why naive square-root-of-time scaling can be inappropriate under fat tails.
- **Expected Shortfall as the primary regulatory measure**: since Basel III shifted toward
  CVaR/Expected Shortfall as the primary market risk measure (partly due to VaR's tail-blindness
  issues this project demonstrates), build out CVaR-focused capital calculations explicitly.
- **GARCH volatility modeling**: replace the constant-volatility assumption with a GARCH(1,1)
  model to capture volatility clustering, and show how time-varying volatility further changes
  VaR estimates.
- **Component/marginal VaR**: decompose portfolio VaR into each asset's marginal contribution,
  useful for understanding which position is driving portfolio-level tail risk.
- **Real market data**: once live data access is available, replace the synthetic dataset with
  real historical asset returns (which will show their own, real fat-tailed characteristics)
  for an actual portfolio risk analysis.
