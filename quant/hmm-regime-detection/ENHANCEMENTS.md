# Potential Enhancements

- **Walk-forward (causally correct) backtest**: re-fit the HMM on a rolling/expanding window
  using only data available up to each point in time, decode only the CURRENT day's regime
  from that point-in-time model, and re-run the exposure strategy - the legitimate version of
  the in-sample demonstration in this project.
- **3+ state models**: extend to 3 states (e.g. Calm / Elevated / Crisis) and evaluate whether
  the additional state improves decoding accuracy or just overfits to noise.
- **Regime-dependent asset allocation**: instead of a simple exposure toggle, use decoded
  regimes to switch between different target portfolios (reusing
  [`quant/portfolio-optimizer-efficient-frontier`](../portfolio-optimizer-efficient-frontier)'s
  optimization for each regime's own return/covariance estimates).
- **Model selection**: fit models with different numbers of states and compare via BIC/AIC to
  determine the statistically justified number of regimes, rather than assuming 2 a priori.
- **Regime persistence probability display**: report the model's implied average regime
  duration (`1/(1-p_stay)`) directly, and compare against the true generating persistence.
- **Multivariate HMM**: extend to fit on multiple observed series simultaneously (e.g. returns
  + realized volatility + a credit spread proxy) rather than returns alone, which typically
  improves regime identification.
- **Real market data**: once live data access is available, fit this model to real historical
  returns and compare the decoded regimes against known historical market stress periods.
