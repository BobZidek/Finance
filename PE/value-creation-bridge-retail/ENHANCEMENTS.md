# Potential Enhancements

- **Alternative attribution order**: add a second bridge that attributes the revenue/margin
  interaction effect the opposite way (margin first, then revenue) and show how much the
  individual bucket sizes shift — reinforcing that the ordering convention is a choice, not
  a law of nature, even though the total is order-independent.
- **Multi-year bridge**: extend from a single entry-to-exit bridge to a year-by-year
  bridge, showing which lever contributed most in which specific year of the hold.
- **Full debt schedule integration**: replace the simplified flat-% debt paydown with the
  detailed interest/tax/capex-driven schedule from the full LBO project for a more precise
  deleveraging contribution.
- **Portfolio-level bridge**: aggregate value creation bridges across multiple portfolio
  companies (reusing the fund model's portfolio structure) to show which lever the fund as a
  whole has relied on most across its entire book — useful for LP-facing "how do we create
  value" narratives.
- **Bad deal case study**: run the same bridge methodology on a deliberately underperforming
  scenario (EBITDA decline, multiple compression) to show how the bridge looks when leverage
  amplifies a loss rather than a gain.
- **Interactive bridge builder**: rebuild as a Streamlit app where entry/exit assumptions can
  be adjusted with sliders and the waterfall chart updates live, with the reconciliation check
  displayed in real time.
