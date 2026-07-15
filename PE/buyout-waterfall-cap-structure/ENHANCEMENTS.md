# Potential Enhancements

- **Non-participating preferred comparison**: add a toggle to run the same deal with
  non-participating preferred (choice of preferred return OR as-converted common, not both)
  and quantify how much that structural choice costs/benefits each class.
- **Option strike price and vesting**: model the option pool with a real strike price
  (rather than $0 cost basis) and a vesting schedule, and only credit vested/exercised options
  at exit.
- **Multiple exit scenarios**: run the waterfall across a range of exit equity values (via
  the entry/exit multiple sensitivity from the quick LBO calculator) to show how each class's
  MOIC changes across upside/downside scenarios — preferred's protection matters most exactly
  when the deal underperforms.
- **Down-case / liquidation scenario**: model a scenario where exit equity value is below the
  preferred's invested capital, showing preferred absorbing all proceeds while common gets zero
  — the protective mechanism working as designed.
- **Multiple management tranches**: add a second management option tranche with a higher
  strike price (an "outperformance" tranche), common in real deals to reward exceeding plan.
- **Full multi-tranche debt schedule**: replace the simplified flat-% debt paydown with the
  detailed interest/tax/capex-driven schedule from the full LBO project for a more precise
  exit equity value.
- **Interactive cap table tool**: rebuild as a small Streamlit app so deal terms (preferred %,
  preferred rate, option pool size) can be adjusted with the waterfall updating live.
