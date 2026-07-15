# Potential Enhancements

- **American (deal-by-deal) waterfall comparison**: build the alternative waterfall structure
  where carry is calculated per-deal rather than whole-fund, and quantify how much earlier
  (and how much more) GP carry would flow under that structure on the same portfolio.
- **GP commitment / co-invest**: model the GP's own capital commitment (typically 1-2% of
  fund size) alongside LP capital, since the GP is usually also an LP-like investor in its
  own fund.
- **GP clawback provision**: model a clawback scenario where later deals underperform after
  the GP has already received catch-up/carry on early winners, and the GP must return excess
  carry to LPs — a real risk in American waterfalls this European structure largely avoids.
- **Multiple fund vintages**: extend to a firm managing several funds (different vintages)
  simultaneously, and show cross-fund LP cash flow and blended firm-level carry.
- **Recycling provision**: model capital recycling (early distributions reinvested into new
  deals rather than returned to LPs during the investment period) common in many fund
  agreements.
- **Follow-on reserves**: reserve a portion of committed capital for follow-on investments
  into existing portfolio companies rather than allocating 100% to new platform deals.
- **Monte Carlo portfolio outcomes**: replace the fixed 8-deal MOIC assumptions with a
  distribution of possible deal outcomes, and simulate a range of fund-level Net IRR/TVPI
  outcomes rather than one deterministic case.
- **XIRR with actual dates**: replace the annual-cashflow bisection IRR with a true XIRR
  using specific call/distribution dates within each year, for more precision.
