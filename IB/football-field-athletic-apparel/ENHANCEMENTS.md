# Potential Enhancements

- **Weighted recommendation**: rather than reporting the raw overall min/max, compute a
  weighted "recommended range" (e.g. 40% precedent transactions, 35% DCF, 25% trading comps)
  reflecting methodology relevance.
- **52-week trading range panel**: add a fourth football field bar showing each peer's
  52-week high/low as a market-sentiment sanity check (a common 4th/5th bar in real decks).
- **Real precedent transaction data**: replace illustrative "Deal A/B/C" labels with real,
  named, sourced M&A transactions once live/historical deal databases are reachable.
- **EV/Revenue football field**: add a second chart using EV/Revenue multiples throughout
  (useful for lower-margin or high-growth targets where EBITDA is less meaningful).
- **Precedent transaction date-weighting**: weight more recent deals more heavily, since
  older deals may reflect stale market conditions.
- **Sensitivity on precedent premium**: strip out the control premium from precedent multiples
  to create a premium-free "adjusted precedent" range comparable to trading comps.
- **Interactive chart**: rebuild the football field as an interactive Plotly chart so a
  recruiter/reader can hover over each bar for the underlying multiple and peer/deal detail.
- **Target scenario toggle**: parameterize target financials via CLI/config so the same
  football field engine can value a different target without code changes.
