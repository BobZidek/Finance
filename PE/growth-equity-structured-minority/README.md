# Growth Equity Structured Minority Investment — Vertex Nutrition Brands

Models a non-control growth equity investment structured as preferred equity with an 8%
cumulative PIK dividend, a 1x non-participating liquidation preference, and a redemption right
that lets the investor force a buyback at the greater of accreted cost or a minimum IRR floor
if no liquidity event occurs within 6 years — the downside-protection mechanics distinctive to
growth equity, sitting between buyout and early-stage VC investing.

For the theory behind PIK accretion, non-participating preferred, and redemption rights, see
[`theory/growth_equity_theory.md`](theory/growth_equity_theory.md).

## What the code does

1. **Loads investment terms** ([`data/investment_assumptions.csv`](data/investment_assumptions.csv))
   — investment amount, as-converted ownership %, PIK dividend rate, liquidation preference
   multiple, minimum IRR redemption floor, and redemption eligibility window.
2. **Loads 3 exit scenarios** ([`data/exit_scenarios.csv`](data/exit_scenarios.csv)) — Strong
   Growth, Modest Growth, and a Stagnant/No-Liquidity-Event redemption scenario.
3. **For each scenario, evaluates all applicable payout paths** — as-converted (common),
   accreted liquidation preference, and (where eligible) redemption value — and selects
   whichever is largest, exactly as a real investor would.
4. **Computes MOIC and IRR** for the chosen path in each scenario.
5. **Outputs**: a scenario comparison CSV, a summary text file, a payout-path comparison chart
   (all three candidate values plotted side by side), and a returns-by-scenario chart.

## Data note

The company and all investment terms are **fictional/illustrative** — a mechanics
demonstration of growth equity structuring rather than an analysis of a real investment.

## How to run

```bash
cd code
pip install -r requirements.txt
python growth_equity_model.py
```

Outputs are written to `output/`.

## Folder structure

```
growth-equity-structured-minority/
├── code/
│   ├── growth_equity_model.py
│   └── requirements.txt
├── data/
│   ├── investment_assumptions.csv
│   └── exit_scenarios.csv
├── theory/
│   └── growth_equity_theory.md
├── output/                  # generated scenario comparison, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Scenario | Chosen Path | Payout | MOIC | IRR |
|---|---|---|---|---|
| Strong Growth ($600mm exit) | As-Converted (common) | $132.0mm | 1.65x | 10.5% |
| Modest Growth ($250mm exit) | Accreted Liquidation Preference | $117.6mm | 1.47x | 8.0% |
| Stagnant / No Liquidity Event | Redemption (IRR floor) | $157.9mm | 1.97x | 12.0% |

- **All three protection mechanisms correctly triggered in exactly the scenario they were
  designed for**: strong growth rewards conversion to common (full upside participation),
  modest growth falls back to the liquidation preference (downside protection), and the
  stagnant scenario triggers redemption at the 12% IRR floor — the strongest protection,
  guaranteeing a minimum *return*, not just a minimum nominal payback.
- This demonstrates exactly why structured minority investing is engineered the way it is:
  each mechanism activates precisely when the others would otherwise leave the investor
  under-protected.
