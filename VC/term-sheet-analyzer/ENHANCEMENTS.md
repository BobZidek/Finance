# Potential Enhancements

- **Multi-round liquidation stack**: extend beyond a single Series B to a full stack of
  preferred rounds (seed, A, B, C) each with their own preference terms, and model the
  seniority order (typically most-recent-round-first, "stacked" preferences) at exit.
- **Anti-dilution overlay**: add broad-based and full-ratchet anti-dilution adjustment
  mechanics and show their impact on payout at a down-round exit scenario.
- **Common/founder ROI view**: convert the common/founder payout chart into an effective
  "price per founder share" metric to make the founder-side impact more concrete than a
  dollar total alone.
- **IRR-based investor comparison**: incorporate time-to-exit and compute IRR (not just MOIC)
  for the investor under each structure, since a faster exit at a lower multiple can beat a
  slower exit at a higher one on an IRR basis.
- **Interactive term sheet negotiator**: rebuild as a Streamlit app where preference multiple,
  cap, and participation toggle can be adjusted live with all three charts updating in real time.
- **Seniority vs. pari passu variations**: model a scenario where Series B is NOT senior to
  Series A (pari passu) and show how splitting a limited preference pool between co-senior
  classes changes the payout curves.
- **Real term sheet benchmarking**: once available, compare the modeled cap/multiple choices
  against real market-standard term sheet data for the relevant stage and sector.
