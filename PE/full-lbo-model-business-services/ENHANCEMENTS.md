# Potential Enhancements

- **Downside stress-test scenario**: add a scenario with a revenue decline or working capital
  spike in an early year to actually force a revolver draw, demonstrating the facility doing
  its job rather than sitting unused.
- **Minimum cash balance / cash sweep %**: add a minimum operating cash balance the sweep must
  respect, and a cash sweep percentage below 100% (this model currently sweeps all available
  cash after mandatory amortization and revolver paydown).
- **Covenant testing**: add a maximum Total Debt/EBITDA and minimum EBITDA/Interest covenant
  check each year, flagging any year where the schedule would breach lender covenants.
- **Multiple exit multiple scenarios**: combine the exit-year comparison with an exit-multiple
  sensitivity (as in the other LBO projects) for a full 2D grid across both hold length and
  exit pricing.
- **Dividend recapitalization**: model a mid-hold dividend recap (drawing incremental Term
  Loan capacity once leverage has fallen enough) to return capital to the sponsor before exit,
  and recompute returns using proper multi-cash-flow XIRR.
- **PIK toggle on Subordinated Notes**: add a payment-in-kind option that lets Sub Notes
  interest accrue to principal instead of being paid in cash, preserving cash for the sweep in
  tight years.
- **Interest rate hedging**: model a portion of the Term Loan at a floating rate with an
  interest rate cap/swap, and show the sensitivity of returns to a rising-rate scenario.
