# Potential Enhancements

- **Combined with participating preferred**: layer this ratchet on top of the sponsor
  preferred/common structure from [`PE/buyout-waterfall-cap-structure`](../buyout-waterfall-cap-structure)
  for a fully integrated cap table and exit waterfall.
- **Vesting schedule**: add a time-based vesting schedule (e.g. 4-year vest with a 1-year
  cliff) so management's ratchet participation is also contingent on continued employment, not
  just deal performance.
- **Individual executive allocation**: split the management pool across multiple named
  executives with different allocation percentages, rather than treating "management" as a
  single pooled participant.
- **Downside/leaver provisions**: model "good leaver" vs. "bad leaver" scenarios (an executive
  departing voluntarily vs. being terminated for cause) and how each affects vested vs.
  unvested ratchet participation.
- **IRR-based ratchet tiers**: replace the MOIC-based tier boundaries with IRR-based ones (or a
  combination), since real deals sometimes use IRR hurdles to also reward faster, not just
  larger, exits.
- **Tax treatment**: model the different tax treatment of management's rollover investment vs.
  their "sweat equity" ratchet participation (often structured to qualify for favorable capital
  gains treatment), a real consideration in MIP design.
- **Continuous (non-tiered) ratchet function**: replace the discrete tier steps with a smooth,
  continuous formula (e.g. management share as a linear or curved function of MOIC) and compare
  incentive dynamics against the stepped version used here.
