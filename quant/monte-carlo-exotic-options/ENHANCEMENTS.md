# Potential Enhancements

- **Variance reduction techniques**: implement antithetic variates and/or control variates
  (using the vanilla option's known closed-form price as a control) to reduce Monte Carlo
  standard error without simply increasing path count.
- **Down-and-in / down-and-out / up-and-in barrier variants**: extend to the other three
  standard barrier option types beyond the up-and-out call modeled here.
- **Geometric average Asian option**: add the geometric-average variant, which (unlike the
  arithmetic average) DOES have a closed-form solution under GBM, providing a second
  independent validation check for the simulation engine, similar in spirit to the vanilla
  call cross-check.
- **American exercise / early exercise features**: extend to path-dependent options with early
  exercise rights, requiring a Least-Squares Monte Carlo (Longstaff-Schwartz) approach.
- **Stochastic volatility**: replace the constant-volatility GBM assumption with a stochastic
  volatility model (e.g. Heston), connecting to the GARCH volatility clustering findings in
  [`quant/garch-volatility-forecasting`](../garch-volatility-forecasting).
- **Greeks via Monte Carlo**: compute Delta, Gamma, and Vega for the exotic options via
  finite-difference bump-and-reprice, extending the Greeks framework from
  [`quant/options-pricing-black-scholes`](../options-pricing-black-scholes) to path-dependent instruments.
- **Real market calibration**: once live data access is available, calibrate volatility to
  real implied volatility surfaces rather than a single flat volatility assumption.
