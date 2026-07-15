# Potential Enhancements

- **Live data feed**: swap the static `fast_food_comps.csv` for a live pull (yfinance, Financial
  Modeling Prep, or Alpha Vantage), with the static CSV kept as an offline fallback/cache.
- **NTM (forward) estimates**: use consensus forward revenue/EBITDA instead of LTM to better
  reflect how the market actually prices growth.
- **Outlier handling**: add an automatic outlier flag/trim (e.g. exclude multiples > 2 standard
  deviations from the median) so a single distorted peer (like SHAK's P/E) doesn't need manual
  interpretation.
- **Regression-based multiples**: regress EV/EBITDA against growth rate and margin across a
  larger peer set to derive a "predicted" multiple for the target instead of a flat percentile
  range — controls for the target not being identical to the peer median.
- **Operating lease adjustment**: incorporate capitalized operating leases into the EV bridge
  (material for restaurant chains with owned vs. leased real estate).
- **Precedent transactions overlay**: add a second panel of historical M&A deals in the sector
  with transaction multiples (which include a control premium) to compare against trading comps.
- **DCF cross-check**: build out IB project #2 (DCF) for the same target and plot both ranges
  on a single football-field chart.
- **Excel output**: generate a formatted, formula-linked `.xlsx` workbook (via `openpyxl`)
  instead of/alongside CSV, matching the deliverable format used on a real desk.
- **Sensitivity/scenario toggle**: parameterize the peer set and target inputs via a config file
  or simple CLI flags so different peer sets or targets can be run without editing code.
- **Automated peer screening**: given a sector/SIC code, auto-pull a candidate peer list and
  apply the size/margin/geography filters described in the theory doc.
