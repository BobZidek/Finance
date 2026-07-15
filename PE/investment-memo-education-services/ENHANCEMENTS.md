# Potential Enhancements

- **Probability-weighted expected return**: assign probabilities to Downside/Base/Upside
  and compute a probability-weighted expected MOIC/IRR rather than presenting three discrete
  points.
- **District funding mix breakdown**: model the target's revenue split between
  federally-funded, state/local-funded, and private-pay segments explicitly, so the downside
  scenario's severity is driven by an actual funding-mix assumption rather than a single
  blended growth-rate shock.
- **Full precedent transactions and trading comps**: add the valuation cross-check exhibits
  from the IB pitch book project (comps, precedent deals) to sanity-check the 8.5x entry
  multiple against market pricing.
- **Formal management assessment scorecard**: quantify the qualitative management assessment
  section using a scoring framework similar to
  [`PE/deal-screening-scorecard`](../deal-screening-scorecard), rather than leaving it purely
  narrative.
- **100-day plan**: add a post-close value creation plan section (specific initiatives,
  owners, timelines) to the memo, standard in a real IC deliverable.
- **PowerPoint/PDF export**: auto-generate the memo as a formatted document (via
  `python-docx` or `python-pptx`) combining the narrative sections and generated charts into
  a single deliverable file.
- **Downside covenant/liquidity check**: verify the downside scenario doesn't breach any
  assumed leverage or coverage covenants, and flag the year(s) where headroom is tightest.
