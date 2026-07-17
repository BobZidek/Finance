# Potential Enhancements

- **Preferred return hurdle on the new fund**: model an explicit 8% preferred return hurdle on
  the continuation fund's own gain (this project simplifies to a straight carry % on the full
  gain), reusing the running preferred-return waterfall logic from
  [`PE/fund-model-waterfall`](../fund-model-waterfall).
- **Multiple assets in the continuation vehicle**: extend from a single-asset deal to a
  multi-asset continuation fund, a common real-world structure, and show how the carry
  crystallization mechanics work across a portfolio.
- **GP co-investment / staple**: model the GP rolling some of its own carried interest or
  co-investing personal capital into the new vehicle (a "GP stapled" commitment), a common
  feature meant to demonstrate continued conflict-of-interest alignment.
- **Status quo option**: model a third LP election option (remaining in the OLD fund on
  existing terms, if a continuation deal doesn't get majority LP support) rather than a forced
  binary roll/cash-out choice.
- **Multiple rolling percentage scenarios**: sensitize the rolling LP % (e.g. 30%-90%) and show
  how new fund capitalization and ownership splits change.
- **Discount to NAV for secondary buyers**: model secondary investors buying in at a discount
  to NAV (common in the broader secondaries market, reflecting illiquidity and diligence risk),
  rather than at par NAV as assumed here.
- **Real transaction benchmarking**: once available, compare this project's carry economics
  against publicly reported terms of real GP-led continuation fund transactions.
