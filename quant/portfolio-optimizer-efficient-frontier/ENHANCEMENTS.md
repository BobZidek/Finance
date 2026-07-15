# Potential Enhancements

- **Position limits**: add per-asset maximum weight constraints (e.g. no single asset above
  30%) to produce more diversified, realistic-looking portfolios and reduce the corner-solution
  effect.
- **Black-Litterman model**: replace the raw historical/assumed expected returns (the most
  unstable input to mean-variance optimization) with a Black-Litterman blend of market-implied
  equilibrium returns and specific investor views.
- **Resampled efficient frontier**: address input sensitivity by resampling the expected
  return/covariance inputs (Monte Carlo) and averaging the resulting frontiers, a standard fix
  for mean-variance optimization's instability.
- **Estimate inputs from real historical data**: once live data access is available, estimate
  expected returns, volatilities, and correlations from actual historical return series instead
  of hand-set assumptions.
- **Shrinkage covariance estimation**: apply Ledoit-Wolf shrinkage to the covariance matrix
  (blending the sample covariance with a structured target) for more stable out-of-sample
  optimization, especially relevant with a larger asset universe.
- **Risk parity comparison**: add a risk-parity portfolio (equal risk contribution from each
  asset) as an alternative construction method and compare its weights and Sharpe ratio against
  the mean-variance portfolios.
- **Rolling out-of-sample backtest**: re-optimize on a rolling window and test how the
  resulting portfolio would have performed out-of-sample, rather than treating this as a
  single static optimization.
