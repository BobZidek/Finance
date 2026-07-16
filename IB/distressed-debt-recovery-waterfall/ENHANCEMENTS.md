# Potential Enhancements

- **Trading price cross-check**: given each tranche's current distressed trading price (if
  available), compute implied market-priced recovery expectations and compare against this
  model's fundamental waterfall — a real distressed desk constantly checks these against each other.
- **DCF-based reorg valuation**: replace the simple EBITDA-multiple reorg EV estimate with a
  full DCF (reusing [`IB/dcf-model-semiconductors`](../dcf-model-semiconductors)'s engine),
  since real reorganization valuations are typically built from a management projection DCF.
- **New debt in the reorganized capital structure**: model a scenario where the reorganized
  company emerges with SOME new debt (not 100% equitized), and how that changes recovery
  allocation for the fulcrum and junior classes.
- **Priming DIP financing**: add debtor-in-possession (DIP) financing as a new super-senior
  claim ahead of even the ABL Revolver, common in real Chapter 11 cases and which further
  dilutes recovery for existing claims.
- **Intercompany/structural subordination**: model a holding-company/operating-company
  structure where some claims are structurally subordinated (issued at a different legal
  entity), a common complexity in real distressed capital structures.
- **Litigation/settlement scenarios**: model a negotiated settlement that deviates from strict
  absolute priority (e.g., "gifting" a small recovery to otherwise-wiped-out equity to secure a
  faster consensual plan), common in practice despite the legal default of absolute priority.
- **Time value of recovery**: discount recoveries received in new debt/deferred instruments
  back to present value, since not all recovery consideration is received as immediate cash.
