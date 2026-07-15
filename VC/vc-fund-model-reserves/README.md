# VC Fund Model — Reserves, Follow-On Decisions & Fund-Level Returns

Simulates a 10-year hypothetical seed-stage VC fund ("Northbridge Venture Partners II")
investing initial checks into 15 portfolio companies, then deploying reserved follow-on
capital into the 5 companies that show enough traction to justify doubling down. Builds
year-by-year capital calls and distributions, runs a no-hurdle 80/20 waterfall (the common VC
fund structure, distinct from the PE fund model's preferred-return waterfall), and computes
fund-level Gross MOIC, LP Net DPI/TVPI, and LP Net IRR.

For the theory behind reserves, follow-on economics, and the no-hurdle waterfall, see
[`theory/reserves_and_followons.md`](theory/reserves_and_followons.md) — **including an
important caveat about how this project's follow-on decisions were constructed.**

## What the code does

1. **Loads fund terms** ([`data/fund_assumptions.csv`](data/fund_assumptions.csv)) — committed
   capital, management fee %, investment period, fund life, carry %.
2. **Loads the portfolio** ([`data/portfolio_companies.csv`](data/portfolio_companies.csv)) —
   15 companies with initial entry year/check/multiple, and (for 5 of them) a follow-on
   check at a later year with its own separate multiple.
3. **Builds year-by-year capital calls** (initial checks + follow-on checks + management fees,
   with the fee stepping down after the investment period) **and gross distributions** (each
   company's total proceeds realized at its exit year).
4. **Runs a no-hurdle waterfall**: 100% return of capital to LPs, then a straight 80/20 split
   — no preferred return tier, unlike the PE fund model.
5. **Computes fund-level metrics**: Gross Fund MOIC, LP Net DPI/TVPI, LP Net IRR (via the same
   bisection-search IRR solver as the PE fund model).
6. **Outputs**: a fund summary, portfolio detail CSV, full waterfall CSV, a J-curve chart, and
   a per-company chart showing initial-check vs. follow-on-check proceeds contribution.

## Data note

The fund and all 15 portfolio companies are **fictional/illustrative**. As explained in the
theory doc, the follow-on decisions were constructed to correlate with eventual success for
pedagogical clarity — real follow-on decisions are made under genuine uncertainty.

## How to run

```bash
cd code
pip install -r requirements.txt
python vc_fund_model.py
```

Outputs are written to `output/`.

## Folder structure

```
vc-fund-model-reserves/
├── code/
│   ├── vc_fund_model.py
│   └── requirements.txt
├── data/
│   ├── fund_assumptions.csv
│   └── portfolio_companies.csv
├── theory/
│   └── reserves_and_followons.md
├── output/                  # generated summary, waterfall, portfolio detail, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Gross Fund MOIC: 4.35x** ($163.2mm proceeds on $37.5mm total invested — $22.5mm initial
  checks + $15mm follow-on checks).
- **LP Net DPI/TVPI: 3.03x, LP Net IRR: 27.5%** — after management fees and $23.4mm of GP carry.
- **The 5 companies that received follow-on capital (33% of the portfolio) generate 95.1% of
  total fund proceeds** — a vivid (if idealized — see the theory doc's caveat) illustration
  of why reserve strategy and follow-on discipline matter as much as initial deal selection.
- The **J-curve** stays negative through Year 6 before turning sharply positive as the largest
  exits (Company 15's follow-on-amplified 40x/6x outcome) land in Years 7-8.
