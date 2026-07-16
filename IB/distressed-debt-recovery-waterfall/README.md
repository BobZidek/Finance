# Distressed Debt Recovery Waterfall & Fulcrum Security Analysis

Distributes an assumed reorganization enterprise value across a hypothetical distressed
retail chain's ("Anchorage Retail Holdings") 6-tranche capital structure in strict absolute-
priority order, identifies the fulcrum security, and sensitizes recovery by tranche across a
range of reorganization enterprise values.

For the theory behind absolute priority and why the fulcrum security is the single most
important concept in distressed investing, see
[`theory/distressed_debt_theory.md`](theory/distressed_debt_theory.md).

## What the code does

1. **Loads the capital structure** ([`data/capital_structure.csv`](data/capital_structure.csv))
   — 6 tranches from super-senior secured ABL Revolver down to Common Equity, each with a par
   claim amount and seniority rank.
2. **Loads reorganization assumptions** ([`data/reorg_assumptions.csv`](data/reorg_assumptions.csv))
   — emergence EBITDA and reorg multiple, used to derive the reorganization enterprise value.
3. **Runs the absolute-priority waterfall**: distributes reorg EV down the capital structure
   in strict seniority order, computing each tranche's dollar recovery and recovery %.
4. **Identifies the fulcrum security** — the tranche where recovery transitions from 100% to a
   partial recovery.
5. **Builds a sensitivity table**: recovery % by tranche across a $300mm-$900mm reorg EV range,
   showing how the fulcrum security itself shifts across different valuation outcomes.
6. **Outputs**: the base case waterfall CSV, sensitivity CSV, a summary text file (with the
   fulcrum security explicitly identified), a base-case waterfall bar chart, and a recovery-
   by-EV line chart.

## Data note

The company and full capital structure are **fictional/illustrative** — a mechanics
demonstration of Chapter 11 recovery waterfall analysis rather than an analysis of a real
restructuring.

## How to run

```bash
cd code
pip install -r requirements.txt
python recovery_waterfall_model.py
```

Outputs are written to `output/`.

## Folder structure

```
distressed-debt-recovery-waterfall/
├── code/
│   ├── recovery_waterfall_model.py
│   └── requirements.txt
├── data/
│   ├── capital_structure.csv
│   └── reorg_assumptions.csv
├── theory/
│   └── distressed_debt_theory.md
├── output/                  # generated waterfall, sensitivity, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Reorganization Enterprise Value: $455mm** vs. **$850mm total funded debt** — a **46.5%
  aggregate impairment**, but with enormous dispersion by tranche.
- **ABL Revolver and First Lien Term Loan recover 100%** ($80mm and $320mm respectively).
- **Second Lien Notes — the fulcrum security — recover only 36.7%** ($55mm of a $150mm claim).
- **Senior Unsecured Notes, Subordinated Notes, and Common Equity all recover $0.**
- The sensitivity analysis shows the fulcrum security itself shifting across the plausible
  reorganization value range — a distressed investor's actual outcome depends heavily on
  which specific tranche they hold, far more than on the company's overall distress level.
