# Potential Enhancements

- **Full multi-tranche debt schedule**: replace the single blended-rate paydown model with the
  detailed Revolver/Term Loan/Subordinated Notes waterfall engine from
  [`PE/full-lbo-model-business-services`](../../PE/full-lbo-model-business-services) for more precision.
- **Covenant headroom analysis**: add explicit maximum leverage and minimum coverage covenants
  (typical in a credit agreement) and check how much headroom remains post-recap in each
  projected year, not just at the moment of the transaction.
- **Formal rating agency methodology**: replace the simplified two-metric scorecard with a
  closer approximation of an actual rating agency's published leveraged finance methodology
  (which weighs additional factors: business risk profile, size, diversification).
- **Multiple recap scenario comparison**: sweep the recap size (e.g. $150mm/$250mm/$350mm) and
  show the IRR-vs-MOIC trade-off curve across different recap magnitudes, not just one point.
- **Market timing sensitivity**: model the new tranche's interest rate as a function of
  prevailing credit market conditions at the recap date, and show how a less favorable
  financing environment changes the recap's attractiveness.
- **Downside stress test**: model a recession scenario post-recap (EBITDA decline) and check
  whether the higher leverage from the recap pushes the company into covenant breach or
  distress — the real risk a dividend recap adds.
- **LP-perspective analysis**: model the recap's impact from the fund's DPI/TVPI perspective
  (an early distribution improves DPI, a fund-reporting metric LPs watch closely), not just
  single-deal sponsor IRR/MOIC.
