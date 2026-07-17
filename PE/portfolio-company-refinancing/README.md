# Portfolio Company Debt Refinancing Analysis — Highland Building Materials LLC

Analyzes an opportunistic debt refinancing for a hypothetical PE-owned portfolio company —
lower rate, extended maturity, **no dividend extraction** (distinct from a dividend recap):
computes annual interest savings, cash refinancing costs, NPV of refinancing, the cash payback
period, and how much achievable-rate cushion exists before refinancing stops making sense.

For the theory behind the NPV framework and how this differs from a dividend recap, see
[`theory/refinancing_theory.md`](theory/refinancing_theory.md).

## What the code does

1. **Loads refinancing assumptions** ([`data/refinancing_assumptions.csv`](data/refinancing_assumptions.csv))
   — outstanding principal, existing and new rates/maturities, OID%, arrangement fees, and
   unamortized old fees.
2. **Computes annual interest savings** and **cash refinancing costs** (OID + arrangement fees).
3. **Computes NPV of refinancing**: present value of interest savings over the existing debt's
   remaining term (the conservative, apples-to-apples comparison window), less cash costs.
4. **Computes the cash payback (breakeven) period** and, via a sensitivity sweep, the
   **breakeven achievable new rate** — how much execution-risk cushion exists.
5. **Outputs**: a summary text file, a rate sensitivity CSV, an NPV-vs-new-rate chart, and an
   NPV bridge waterfall chart.

## Data note

The company and all financial terms are **fictional/illustrative** — a mechanics
demonstration of refinancing analysis rather than an analysis of a real transaction.

## How to run

```bash
cd code
pip install -r requirements.txt
python refinancing_model.py
```

Outputs are written to `output/`.

## Folder structure

```
portfolio-company-refinancing/
├── code/
│   ├── refinancing_model.py
│   └── requirements.txt
├── data/
│   └── refinancing_assumptions.csv
├── theory/
│   └── refinancing_theory.md
├── output/                  # generated summary, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Annual interest savings: $6.00mm** (150bps improvement on $400mm principal, 9.25% → 7.75%).
- **Cash refinancing costs: $3.50mm** (OID + arrangement fees).
- **NPV of refinancing: $16.48mm** over the existing debt's 4-year remaining term — strongly
  NPV-positive.
- **Cash payback period: just 0.58 years (~7 months)** — refinancing costs recoup almost
  immediately.
- **Breakeven achievable rate: 8.98%** — 27bps of cushion below the existing 9.25% rate,
  meaning the refinancing remains NPV-positive even if actual market execution comes in worse
  than the targeted 7.75%.
