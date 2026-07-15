# Full Investment Memo — Education Services

The PE capstone project: a full multi-tranche LBO (Revolver + Term Loan + Subordinated Notes)
for a hypothetical K-12 supplemental education platform ("Horizon Learning Partners"), run
across Downside / Base / Upside scenarios, packaged with the market analysis, risk factors,
and management assessment sections of a real investment committee memo.

**The actual memo is in [`theory/investment_memo_narrative.md`](theory/investment_memo_narrative.md)**
— read that for the full IC memo (executive summary, industry overview, risk factors,
management assessment, valuation, recommendation). This README covers the quantitative engine
behind it.

## What the code does

1. **Loads deal assumptions** ([`data/lbo_assumptions.csv`](data/lbo_assumptions.csv)) — the
   same Revolver + Term Loan + Subordinated Notes structure as
   [`PE/full-lbo-model-business-services`](../full-lbo-model-business-services).
2. **Loads three scenarios' forecast drivers** ([`data/scenario_drivers.csv`](data/scenario_drivers.csv))
   — Downside (models an ESSER federal funding cliff: a Year-2 revenue decline and margin
   compression), Base, and Upside.
3. **Runs the full debt schedule** (interest on beginning balances, mandatory Term Loan
   amortization, revolver draw-if-short / paydown-first-if-cash-positive, cash sweep) for
   each scenario independently.
4. **Computes 5-year sponsor MOIC/IRR per scenario**, plus an **Entry x Exit multiple
   sensitivity grid** on the base case.
5. **Outputs**: a quantitative summary, per-scenario debt schedule CSVs, a scenario
   summary CSV, a scenario comparison chart (MOIC bars + IRR line), and a sensitivity heatmap.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs**. The
ESSER funding cliff referenced in the downside scenario and the memo narrative is a real,
well-documented, sector-wide phenomenon (the wind-down of federal COVID-era education relief
funding) — included here as a general industry risk factor, not a claim about any specific
company.

## How to run

```bash
cd code
pip install -r requirements.txt
python investment_memo_model.py
```

Outputs are written to `output/`.

## Folder structure

```
investment-memo-education-services/
├── code/
│   ├── investment_memo_model.py
│   └── requirements.txt
├── data/
│   ├── lbo_assumptions.csv
│   └── scenario_drivers.csv
├── theory/
│   └── investment_memo_narrative.md   <- the actual IC memo
├── output/                  # generated summary, scenario schedules, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Scenario | Exit EBITDA | Exit Equity | MOIC | IRR |
|---|---|---|---|---|
| Downside | $34.2mm | $169.8mm | 1.67x | 10.9% |
| Base | $48.5mm | $338.9mm | 3.34x | 27.3% |
| Upside | $59.0mm | $455.5mm | 4.49x | 35.0% |

- Even the **Downside scenario (ESSER funding cliff shock) remains capital-accretive**
  (1.67x MOIC) — a meaningful underwriting finding, since it means the deal's downside case
  doesn't require a bailout scenario to avoid a loss.
- The **base-case Entry x Exit multiple sensitivity** ranges from **12.1% IRR** (paying up at
  10.0x entry, selling at a compressed 7.5x) to **51.0% IRR** (buying at a disciplined 7.0x,
  selling at 10.5x) — entry price discipline matters as much as the scenario itself.
- See the full narrative memo for the industry, risk, and management sections that turn this
  quantitative output into an actual investment recommendation.
