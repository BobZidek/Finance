# Potential Enhancements

- **Pro-rata rights**: model existing investors exercising pro-rata rights in later rounds to
  maintain their ownership %, and show how that changes new-investor allocation.
- **Multiple SAFEs with different seniority/MFN clauses**: add a Most Favored Nation clause
  where an earlier SAFE can claim the better terms of a later SAFE, and model the resulting
  conversion price adjustment.
- **Liquidation preference stack**: layer in each priced round's liquidation preference terms
  (feeding into [`VC/term-sheet-analyzer`](../term-sheet-analyzer)) so the cap table shows both
  fully-diluted ownership AND what each class would actually receive at a given exit value.
- **Vesting schedules**: add founder and option pool vesting schedules (4-year, 1-year cliff)
  so unvested shares can be distinguished from vested/exercised shares at any point in time.
- **Secondary sales**: model a secondary transaction (existing holder sells shares to a new or
  existing investor) and show how it affects the cap table without creating new dilution.
- **Interactive cap table builder**: rebuild as a Streamlit app where rounds can be added/edited
  with the dilution chart updating live — closer to how founders actually plan financing.
- **Down round / pay-to-play scenario**: model a down round (new round priced below the prior
  round) and its interaction with any anti-dilution provisions from earlier rounds.
