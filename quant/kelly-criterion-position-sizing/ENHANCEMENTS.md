# Potential Enhancements

- **Continuous (investment) Kelly**: extend from the discrete binary-bet formula to the
  continuous version for a normally-distributed return asset (`f* = (mu - r) / sigma^2`),
  directly connecting Kelly sizing to portfolio allocation in
  [`quant/portfolio-optimizer-efficient-frontier`](../portfolio-optimizer-efficient-frontier).
- **Uncertain edge estimation**: model the realistic scenario where the true win probability
  isn't known with certainty but must be estimated from limited historical data, and show how
  Kelly sizing should be more conservative when the edge estimate itself is uncertain
  ("Kelly with parameter uncertainty").
- **Multiple simultaneous bets/positions**: extend from a single sequential bet to Kelly sizing
  across a portfolio of simultaneous, correlated positions, a genuinely harder multi-asset
  Kelly problem.
- **Transaction costs**: add a per-bet cost that erodes the edge, and show how the Kelly-
  optimal fraction (and whether betting at all is even worthwhile) changes once costs are included.
- **Drawdown-constrained Kelly**: solve for the largest bet fraction subject to an explicit
  maximum acceptable risk-of-ruin constraint, rather than choosing an ad hoc fraction (like Half
  Kelly) of the theoretical optimum.
- **Fractional Kelly sweep**: run the simulation across a continuous sweep of Kelly fractions
  (e.g. 0.1x to 3x) rather than four discrete points, to show the full growth-rate-vs-risk
  trade-off curve.
- **Real trading strategy application**: once available, apply this framework to a real
  strategy's actual historical win rate and payoff ratio for genuine position sizing guidance.
