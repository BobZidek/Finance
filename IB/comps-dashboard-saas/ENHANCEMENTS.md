# Potential Enhancements

- **Live data pipeline**: wire up the existing `yfinance` code path to actually pull EV,
  revenue, growth, and FCF margin live (with the static CSV kept as an offline cache/fallback),
  and schedule periodic refreshes.
- **Multi-factor regression**: add FCF margin (or the Rule of 40 score) as a second independent
  variable — a multiple regression `EV/Revenue = β₀ + β₁×Growth + β₂×FCFMargin` would likely
  explain meaningfully more variance than growth alone (R² > 0.64) and produce more precise
  over/undervalued flags.
- **Sector expansion**: broaden the "software" peer set into named sub-sectors (infrastructure/
  DevOps, cybersecurity, vertical SaaS, horizontal productivity) and let the dashboard flag
  which sub-sector currently trades richest/cheapest.
- **NTM (forward) estimates**: use forward revenue growth and forward EV/Revenue instead of
  LTM, which better reflects how the market is actually pricing near-term expectations.
- **Confidence intervals on the regression line**: plot a prediction interval band around
  the fitted line (not just the point estimate) so the target's implied multiple carries an
  explicit range, not a single number.
- **Automated screening across sectors**: parameterize the peer universe by sector/SIC code
  so the same regression engine can run on any sector (not just SaaS) without code changes.
- **Interactive dashboard**: rebuild as a Streamlit or Plotly Dash app so a recruiter can
  filter the peer set, toggle the regression driver variable, and see the target's implied
  valuation update live.
