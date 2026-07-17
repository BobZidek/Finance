# Potential Enhancements

- **Greenshoe via short-covering**: model the alternative (non-dilutive) greenshoe mechanism,
  where underwriters cover the over-allotment via open-market purchases rather than drawing
  additional primary shares from the company, and compare dilution outcomes.
- **Lock-up expiration modeling**: add a 180-day lock-up schedule and model the potential
  supply/price impact when a large tranche of previously-restricted shares becomes sellable.
- **Use of proceeds detail**: break down net primary proceeds into specific uses (debt paydown,
  growth capex, working capital, M&A reserve) rather than a single lump sum.
- **Regression-based comps**: replace the flat multiple range with the growth-adjusted
  regression approach from [`IB/comps-dashboard-saas`](../comps-dashboard-saas) for a more
  precise intrinsic valuation given the company's specific growth rate.
- **First-day trading simulation**: model a range of possible first-day closing prices (not
  just the intrinsic midpoint) and the resulting range of money-left-on-the-table outcomes.
- **Multiple share classes**: model dual-class share structures (common in tech IPOs, giving
  founders enhanced voting rights) and their effect on post-IPO control vs. economic ownership.
- **Direct listing comparison**: model a direct listing (no primary shares, no underwriting
  discount, no lock-up) as an alternative to a traditional IPO, and compare the trade-offs.
