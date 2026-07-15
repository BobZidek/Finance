# Potential Enhancements

- **Monte Carlo simulation**: replace the fixed 20-outcome portfolio with a random draw from
  a fitted power-law (Pareto) distribution across many simulated portfolios, to show the range
  of fund-level MOIC outcomes a given check-size/portfolio-size strategy might produce.
- **Reserve strategy integration**: connect to [`VC/vc-fund-model-reserves`](../vc-fund-model-reserves)
  to show how following on into apparent winners (rather than deploying reserves evenly)
  changes the concentration and overall fund MOIC.
- **Check size sensitivity**: compare a "spray and pray" strategy (40 smaller checks) against
  a "concentrated conviction" strategy (10 larger checks) on the same underlying company
  universe, and show how portfolio size affects the odds of catching an outlier.
- **Time-weighted (IRR) view**: add entry/exit years per investment and compute portfolio IRR,
  not just MOIC, since the power law's timing (an early fund returner vs. a late one) matters
  for actual LP returns.
- **Ownership-weighted concentration**: incorporate different ownership %s per investment
  (rather than assuming identical check sizes) to reflect realistic pro-rata and follow-on
  dynamics.
- **Sector/stage breakdown**: tag each investment by sector and entry stage, and show whether
  power-law concentration differs across those cuts.
- **Benchmark against real fund return data**: once available, compare this portfolio's
  concentration statistics against published VC fund return studies (e.g. Correlation Ventures'
  power law research) for calibration.
