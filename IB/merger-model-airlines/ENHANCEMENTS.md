# Potential Enhancements

- **Debt paydown / FCF sweep**: model actual free cash flow generation and debt paydown
  post-close (borrowing the LBO project's waterfall logic) instead of holding deal debt flat,
  so leverage deleverages faster and more realistically.
- **Purchase price allocation & incremental D&A**: model intangible asset step-ups (e.g. gate
  slots, loyalty program value, routes) and the resulting incremental amortization.
- **Fleet/network overlap detail**: for an airline-specific enhancement, break the cost synergy
  bucket into named categories (fleet rationalization, MRO consolidation, corporate overhead,
  distribution) with separate realization curves for each.
- **Regulatory/DOJ risk adjustment**: airline mergers face significant antitrust scrutiny;
  add a scenario for mandated slot/gate divestitures and their EBITDA impact.
- **5-year (not 3-year) horizon**: extend the ramp and pro forma further out, since some
  synergies (fleet commonality, IT system consolidation) take longer than 3 years to fully realize.
- **Exchange ratio / collar mechanics**: for the stock consideration, model a fixed exchange
  ratio and a collar range instead of a flat percentage of deal value.
- **Credit rating impact model**: map the pro forma leverage trajectory to an approximate
  credit rating band and flag if the deal risks a downgrade.
- **Monte Carlo on synergies**: replace the discrete 50%-150% grid with a full probability
  distribution over synergy realization to generate a distribution of Year-3 accretion outcomes.
