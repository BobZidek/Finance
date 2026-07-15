# Potential Enhancements

- **Longer sample / lower-persistence sensitivity**: rerun with a longer history and/or a
  lower spread AR(1) persistence parameter to show the `coint()` test achieving clear
  significance, directly demonstrating the sample-size and persistence effects discussed in
  the theory doc.
- **Rolling out-of-sample cointegration monitoring**: re-test cointegration on a rolling
  window through the backtest period, since a pair's relationship can break down over time -
  a real pairs desk continuously re-validates, not just once at the start.
- **Dynamic (rolling) hedge ratio and z-score**: replace the full-sample hedge ratio and
  z-score with rolling-window estimates, more realistic for live trading than using
  full-sample statistics that include future data relative to any given trading day.
- **Multiple candidate pairs screening**: extend from a single pair to a universe of
  candidate pairs, screening for the ones with the strongest, most significant cointegration
  before trading - the realistic starting point for a pairs trading strategy.
- **Transaction costs and short-selling costs**: add realistic costs (including borrow costs
  for the short leg) to the backtest, which can meaningfully erode returns for a
  frequently-trading mean-reversion strategy.
- **Kalman filter hedge ratio**: replace the static OLS hedge ratio with a time-varying
  estimate via a Kalman filter, a common refinement in production pairs trading systems.
- **Real market data**: once live data access is available, screen and test real candidate
  pairs (e.g. within the same sector) instead of synthetic data.
