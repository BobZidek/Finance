# Potential Enhancements

- **Cash vs. PIK dividend toggle**: model a hybrid where the company can pay the dividend in
  cash when it has sufficient liquidity and PIK otherwise, rather than a pure PIK assumption.
- **Anti-dilution protection**: add a broad-based weighted-average anti-dilution adjustment for
  a scenario where the company raises a future down round, reusing concepts from
  [`VC/cap-table-dilution-tracker`](../../VC/cap-table-dilution-tracker).
- **Board/governance rights modeling**: add a qualitative section on the minority protective
  provisions (board observer/seat rights, veto rights over major decisions) that typically
  accompany a structured minority investment alongside the economic terms modeled here.
- **Partial redemption**: model a scenario where the company can only afford to redeem a
  portion of the preferred position, with the remainder continuing to accrue, rather than an
  all-or-nothing redemption assumption.
- **Multiple investment tranches**: model a staged investment (e.g. an initial tranche plus a
  contingent follow-on tranche tied to milestones), common in larger growth equity rounds.
- **Probability-weighted expected return**: assign probabilities to each exit scenario and
  compute a probability-weighted expected MOIC/IRR across the full distribution of outcomes.
- **Comparison against a plain common equity investment**: run the same $80mm check as
  unstructured common equity (no preference, no redemption) and quantify exactly how much
  downside protection the structured terms are worth across the scenario set.
