# Potential Enhancements

- **Revolver / minimum cash balance**: add a revolving credit facility that draws if FCF is
  insufficient to cover mandatory debt service, and a minimum cash balance the sweep respects.
- **Add-on acquisitions (roll-up mechanic)**: since this is a healthcare *roll-up*, model
  periodic bolt-on acquisitions funded by incremental debt/FCF during the hold period, each
  contributing incremental EBITDA at its own entry multiple — the core roll-up value driver.
- **Management rollover / option pool**: model management rolling a portion of proceeds into
  the new equity and an option pool, diluting sponsor MOIC/IRR realistically.
- **Dividend recapitalization**: add a mid-hold dividend recap scenario (raise incremental debt
  post-deleveraging to return capital to the sponsor early) and recompute IRR using true
  multi-cash-flow XIRR instead of the single entry/exit MOIC^(1/n) shortcut.
- **PIK toggle notes**: model a payment-in-kind option on the subordinated tranche (interest
  accrues to principal instead of being paid in cash) to preserve FCF for the sweep.
- **Covenant testing**: add a leverage/coverage covenant check (e.g. max Total Debt/EBITDA,
  min EBITDA/Interest) each year and flag any breach.
- **Monte Carlo returns**: randomize revenue growth and exit multiple across distributions to
  produce a full IRR probability distribution instead of a single 5x5 grid.
- **Real deal data**: replace the fictional target with a real (or realistic anonymized)
  healthcare services roll-up once live/comparable transaction data is reachable.
