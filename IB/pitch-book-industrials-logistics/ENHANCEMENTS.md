# Potential Enhancements

- **Full narrative sections**: expand the industry overview and company overview into actual
  written pitch book pages (market sizing, competitive positioning maps, management assessment)
  rather than the condensed paragraph in the theory doc.
- **Synergy-adjusted strategic buyer range**: add a fifth football field bar modeling what a
  *strategic* acquirer's ability-to-pay looks like once realistic synergies are layered on top
  of the LBO ability-to-pay engine (reusing the merger model's synergy-ramp logic).
- **Weighted core range**: instead of a simple two-method overlap, compute a formal weighted
  average across all four methods with explicit, stated weights.
- **Real deal / real target data**: replace the illustrative comps, precedent transactions,
  and fictional target with real, sourced data once live financial data access is available.
- **Process recommendation detail**: model an indicative buyer universe (strategic vs. sponsor
  count, likely bid ranges) and a process timeline (auction vs. negotiated sale) alongside the
  valuation.
- **PowerPoint/PDF export**: auto-generate an actual slide deck (via `python-pptx`) from the
  computed tables and charts, matching the visual format of a real pitch book deliverable.
- **Cross-check against precedent LBOs**: since precedent transactions include financial-sponsor
  deals, cross-check whether the ability-to-pay ceiling here is consistent with the leverage/
  multiples actually seen in sponsor-led precedent deals in the dataset.
- **Sector-specific KPIs**: add logistics-specific operating metrics (load-to-truck ratio,
  on-time delivery rate, revenue per mile) to the company overview section for realism.
