# Potential Enhancements

- **Multiple exit scenarios with probabilities**: replace the single assumed exit value with
  a probability-weighted set of exit scenarios (IPO, strategic acquisition, acqui-hire,
  shutdown) and compute an expected-value pre-money valuation.
- **Bottoms-up exit value cross-check**: derive the assumed exit value from a forward
  revenue/EBITDA multiple applied to a projected exit-year financial forecast (reusing the
  comps methodology from the IB projects), rather than assuming it directly.
- **Option pool impact**: incorporate an option pool top-up into the ownership math for this
  round itself, similar to [`VC/cap-table-dilution-tracker`](../cap-table-dilution-tracker),
  since that also affects required ownership and valuation.
- **Time-value discounting**: discount the required ROI itself by the years-to-exit and an
  assumed risk-free/hurdle rate, distinguishing "required money multiple" from "required IRR"
  explicitly (a 15x return over 4 years implies a much higher IRR than the same 15x over 8 years).
- **Comparable early-stage round benchmarking**: cross-check the resulting valuation against
  typical seed/Series A valuation ranges for comparable-stage companies once live market data
  is reachable.
- **Convert to SAFE terms**: translate the resulting pre/post-money valuation into an
  equivalent SAFE valuation cap, for cases where this round is being structured as a SAFE
  rather than a priced round.
