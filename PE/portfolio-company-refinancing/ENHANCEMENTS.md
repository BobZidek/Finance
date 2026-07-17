# Potential Enhancements

- **Prepayment penalty modeling**: add a call premium (e.g. 101 soft call) on the existing debt
  if it's still within its call protection period, a common real-world cost this project
  assumes is already zero.
- **Multi-tranche refinancing**: extend from a single term loan to a full capital structure
  refinancing (Term Loan + Subordinated Notes), reusing the multi-tranche framework from
  [`PE/full-lbo-model-business-services`](../full-lbo-model-business-services).
- **Floating rate / hedging analysis**: model the existing and new debt as floating-rate
  (SOFR + spread) rather than a fixed all-in rate, and add an interest rate cap/swap decision
  alongside the refinancing decision.
- **Covenant package comparison**: compare the covenant packages (leverage/coverage tests,
  restricted payment baskets) of the old vs. new debt, since refinancings often also
  renegotiate covenant flexibility, not just pricing.
- **Combined refinancing + dividend recap**: model a transaction that both refinances at
  better terms AND upsizes the facility to fund a partial dividend, combining this project's
  mechanics with [`IB/dividend-recap-credit-analysis`](../../IB/dividend-recap-credit-analysis).
- **Credit rating impact**: model how the improved rate and extended maturity affect the
  company's implied credit profile, reusing the rating scorecard from the dividend recap project.
- **Real market pricing**: once live credit market data access is available, calibrate the
  achievable new rate against actual current leveraged loan market pricing for comparable credits.
