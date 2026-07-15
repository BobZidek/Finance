# Potential Enhancements

- **Multi-period panel backtest**: extend from a single cross-sectional snapshot to many
  periods (a full panel), computing IC each period and reporting the mean/std of IC over time
  (IC Information Ratio) — the standard, more rigorous way factor research is actually evaluated.
- **Realistic signal-to-noise calibration**: rerun with a signal-to-noise ratio closer to real
  single-period factor effect sizes (much weaker than this project's) and show how much larger
  a sample (more stocks, more periods) is needed to detect it reliably.
- **Factor correlation and orthogonalization**: model factors as correlated (as real Value and
  Momentum often are) and orthogonalize them (regress one out of another) before combining, to
  avoid double-counting overlapping signal.
- **Weighted composite optimization**: instead of an equal-weighted composite, optimize factor
  weights to maximize historical IC or Sharpe ratio (with appropriate out-of-sample validation
  to avoid overfitting).
- **Transaction cost-aware long-short portfolio**: build the actual long-short portfolio
  (not just quintile average returns) with position sizing and realistic transaction costs,
  reusing the approach from [`quant/ml-return-prediction`](../ml-return-prediction).
- **Additional factors**: add size, low-volatility, and profitability-growth factors, common
  in institutional multi-factor models.
- **Real fundamental/price data**: once live data access is available, replace the synthetic
  dataset with real P/E, momentum, and ROE data for an actual universe of stocks.
