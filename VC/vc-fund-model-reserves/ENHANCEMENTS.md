# Potential Enhancements

- **Follow-on decisions under uncertainty**: instead of allocating follow-ons with perfect
  hindsight, model a realistic signal (e.g. Series A revenue multiple, growth rate) with noise,
  and simulate follow-on decisions made on that imperfect signal — including some decisions
  that turn out wrong (following on into a company that later fails, or passing on one that
  later succeeds).
- **Pro-rata rights modeling**: distinguish between exercising a pro-rata right (maintaining
  existing ownership %) versus a "super pro-rata" follow-on (increasing ownership), since real
  fund documents often specify pro-rata rights explicitly.
- **Preferred-return variant comparison**: run the same portfolio through a hurdle-based
  European waterfall (like the PE fund model) and quantify exactly how much GP carry timing
  and total amount differ between the no-hurdle and hurdle structures.
- **Reserve ratio sensitivity**: sweep the reserve % of committed capital (e.g. 30% vs. 50% vs.
  70%) holding the same initial check strategy, and show how fund-level MOIC changes if more
  or less capital is available for follow-ons into winners.
- **Multiple fund vintages / recycling**: model a fund recycling early distributions into new
  first checks during the investment period, common in some VC fund structures.
- **Monte Carlo portfolio outcomes**: combine with the power-law model's Monte Carlo
  enhancement to simulate a distribution of possible fund-level outcomes across many random
  portfolio draws, rather than one deterministic case.
- **GP co-investment / fund-of-one**: model a scenario where the GP also invests personal
  capital alongside the fund into follow-on rounds, and how that affects the carry calculation.
