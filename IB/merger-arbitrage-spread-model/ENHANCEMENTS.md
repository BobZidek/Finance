# Potential Enhancements

- **Stock/mixed consideration deals**: extend beyond an all-cash deal to a stock-for-stock or
  mixed cash-and-stock deal, where the spread also depends on the acquirer's own share price
  movement, adding a second source of risk to hedge.
- **Multiple downside scenarios**: replace the single "downside if broken" price with a
  probability-weighted range of break scenarios (e.g., a competing bidder emerges vs. a clean break).
- **Regulatory timeline modeling**: add explicit antitrust review stage tracking (HSR waiting
  period, second request, litigation risk) with stage-specific probability updates as a deal progresses.
- **Portfolio-level merger arb**: extend from a single deal to a portfolio of multiple pending
  deals, and show how diversification reduces the impact of any single deal breaking, reusing
  concentration/diversification concepts from [`VC/portfolio-power-law-model`](../../VC/portfolio-power-law-model).
- **Historical spread tracking**: model how the spread and implied probability evolve over
  time from announcement to close, rather than a single point-in-time snapshot.
- **Financing risk decomposition**: for leveraged deals, model the risk that acquirer financing
  falls through separately from regulatory/shareholder approval risk, since they have different
  risk profiles and timelines.
- **Real deal data**: once live market data access is available, apply this framework to a
  real, currently pending M&A deal.
