# Potential Enhancements

- **Fat-tailed innovations**: fit GARCH with Student-t distributed innovations (instead of
  normal) to combine time-varying volatility with fat tails simultaneously, connecting directly
  to the distributional lesson from [`quant/risk-model-var-cvar`](../risk-model-var-cvar).
- **GARCH-based VaR**: feed the GARCH conditional volatility forecast into a parametric VaR
  calculation instead of a constant historical volatility, and compare backtested exceedance
  rates against the risk model project's static-volatility parametric VaR.
- **Model comparison**: fit and compare EGARCH (captures asymmetric volatility response to
  positive vs. negative shocks - the "leverage effect") and GJR-GARCH against the standard
  GARCH(1,1) used here.
- **Longer forecast horizon and confidence bands**: extend the forecast beyond 20 days and add
  confidence intervals around the volatility forecast, not just a point estimate.
- **Rolling out-of-sample re-fitting**: re-fit the GARCH model on a rolling window through the
  sample and evaluate true out-of-sample forecast accuracy, rather than fitting once on the
  full sample.
- **Multivariate GARCH**: extend to a multi-asset DCC-GARCH (Dynamic Conditional Correlation)
  model to capture time-varying correlations, not just time-varying individual volatilities -
  relevant for the portfolio optimizer and risk model projects.
- **Real market data**: once live data access is available, fit GARCH to real historical
  returns and compare the fitted persistence and volatility clustering against this project's
  synthetic benchmark.
