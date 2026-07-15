# Potential Enhancements

- **Larger universe**: expand from 10 to 50-100+ candidates (a more realistic sourcing
  funnel size) and add a configurable cutoff (e.g. top decile) rather than a fixed top-3.
- **Sector-relative scoring**: compute z-scores within each sector rather than across the
  whole universe, since "good margin" means something different in software vs. distribution
  — currently a chemicals company's high margin may just reflect sector norms, not
  outperformance.
- **Weight sensitivity**: sweep the scoring weights across plausible ranges and show how
  robust the top-3 shortlist is to different investment theses (growth-focused vs.
  quality/leverage-focused weighting).
- **Qualitative overlay**: add a manually-scored qualitative factor (management quality,
  competitive moat, ESG considerations) as a 6th weighted input alongside the quantitative
  metrics.
- **Live data sourcing**: pull the target universe from a real screening database/API
  (PitchBook, Capital IQ) instead of a static CSV, once available.
- **Outlier/data-quality flags**: flag any target with a metric more than 2-3 standard
  deviations from the mean for a manual data-quality double-check before trusting its score.
- **Valuation overlay**: cross-reference the top-ranked names against implied valuation
  (using the comps/DCF engines from the IB projects) to screen for both quality *and* an
  attractive entry price.
