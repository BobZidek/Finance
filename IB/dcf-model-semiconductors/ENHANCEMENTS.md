# Potential Enhancements

- **Live/actual financials**: replace hand-set assumptions with TXN's actual 10-K figures
  and sell-side consensus estimates for revenue growth and margins.
- **Levered FCF / equity DCF variant**: build a second version discounting levered FCF at
  cost of equity directly, and compare implied prices against the unlevered approach.
- **Multi-stage growth**: replace the single Gordon Growth terminal value with a two-stage
  or fade-period model (e.g. 5 years explicit + 5 years fading to terminal growth) to reduce
  the % of EV coming from the terminal value.
- **Exit multiple cross-check**: compute terminal value a second way using an EV/EBITDA exit
  multiple (from the comps project) and compare against the Gordon Growth terminal value —
  a standard sanity check on a real desk.
- **Monte Carlo sensitivity**: instead of a static grid, randomly sample WACC, terminal growth,
  and margin assumptions from distributions to produce a full implied-price probability
  distribution rather than a 5x5 grid.
- **Scenario cases**: add explicit bull/base/bear driver sets (optimistic/base/pessimistic
  revenue growth and margin paths) rather than a single base case.
- **Football field integration**: plot the DCF range alongside the comps-derived valuation
  range (IB project #1) and precedent transaction multiples on one chart.
- **Beta regression**: compute beta directly from historical stock returns vs. a market index
  instead of using an assumed input.
- **Excel output**: rebuild as a fully formula-linked `.xlsx` model (via `openpyxl`) with the
  sensitivity table as a native Excel data table, matching the deliverable format used on a
  real desk.
