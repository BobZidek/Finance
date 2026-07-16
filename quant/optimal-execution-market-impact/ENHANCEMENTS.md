# Potential Enhancements

- **Discrete-time exact kappa**: replace the continuous-time kappa approximation with the
  exact discrete-time formula (`kappa = (1/tau) x arccosh(0.5 x (kappa_tilde x tau)^2 + 1)`)
  for more precision when the number of periods is small.
- **Real market impact calibration**: once live data access is available, calibrate the
  temporary and permanent impact coefficients against real historical execution data (e.g.,
  via a transaction cost analysis / TCA dataset) instead of illustrative values.
- **Participation rate constraints**: add a maximum participation rate (e.g., never trade more
  than 20% of expected volume in a single period) as an explicit constraint on the trajectory,
  common in real execution algorithms.
- **Adaptive/reactive execution**: extend from a static pre-computed trajectory to an adaptive
  strategy that adjusts trading rate in response to realized price moves during execution,
  rather than committing to a fixed schedule upfront.
- **Multi-asset execution**: extend to simultaneously liquidating a basket of correlated
  positions, where cross-asset correlation affects the optimal joint trajectory - connecting to
  the portfolio-level thinking in [`quant/portfolio-optimizer-efficient-frontier`](../portfolio-optimizer-efficient-frontier).
- **Alternative impact functions**: replace the linear (in trading rate) temporary impact
  assumption with a more realistic square-root impact model, commonly found to fit real market
  impact data better than the linear model used here.
- **Implementation shortfall decomposition**: decompose realized execution cost into its
  market impact, timing risk, and opportunity cost components after the fact, for a real
  post-trade transaction cost analysis.
