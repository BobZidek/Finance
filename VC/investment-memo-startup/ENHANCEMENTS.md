# Potential Enhancements

- **Probability-weighted expected return**: assign probabilities to Bear/Base/Bull and compute
  a probability-weighted expected MOIC/IRR rather than presenting three discrete points.
- **Full cap table integration**: build out the actual post-Series-A cap table (reusing
  [`VC/cap-table-dilution-tracker`](../cap-table-dilution-tracker)'s engine) instead of a
  single blended retention ratio assumption.
- **Term sheet detail**: layer in the actual liquidation preference structure for this round
  (reusing [`VC/term-sheet-analyzer`](../term-sheet-analyzer)) so the Bear-case payout reflects
  preference protection rather than pure as-converted math.
- **SaaS metrics trend**: extend the current-ARR snapshot into a quarterly historical build
  (reusing [`VC/saas-metrics-dashboard`](../saas-metrics-dashboard)'s approach) to show the
  trajectory of NRR and burn multiple leading up to this round, not just a point-in-time figure.
- **Portfolio construction context**: model where this specific investment would sit within a
  broader fund portfolio (reusing [`VC/portfolio-power-law-model`](../portfolio-power-law-model))
  to assess whether it's sized appropriately relative to its role in overall fund returns.
- **Reference checks / diligence tracker**: add a structured diligence checklist section
  (technical, customer, team reference checks) with status tracking, standard in a real
  pre-IC diligence process.
- **PowerPoint/PDF export**: auto-generate the memo as a formatted document combining the
  narrative sections and generated charts into a single deliverable file.
