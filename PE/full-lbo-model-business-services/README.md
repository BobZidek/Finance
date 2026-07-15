# Full LBO Model with Revolver — Business Services

A detailed 7-year LBO debt schedule for a hypothetical outsourced business services / BPO
company ("Vertex Business Solutions") — three tranches (Revolver, Term Loan, Subordinated
Notes) with a full cash sweep waterfall — plus a direct comparison of sponsor IRR/MOIC across
three candidate exit years (3 / 5 / 7).

For the theory behind the revolver mechanics and the MOIC-vs-IRR exit timing tradeoff, see
[`theory/revolver_and_exit_timing.md`](theory/revolver_and_exit_timing.md).

## What the code does

1. **Loads deal assumptions** ([`data/lbo_assumptions.csv`](data/lbo_assumptions.csv)) — entry
   revenue/EBITDA, entry/exit multiples, revolver capacity/rate/commitment fee, Term Loan and
   Subordinated Notes sizing (EBITDA turns) and pricing, tax rate.
2. **Loads forecast drivers** ([`data/forecast_drivers.csv`](data/forecast_drivers.csv)) —
   7 years of revenue growth, EBITDA margin, D&A%, capex%, and NWC-as-%-of-revenue.
3. **Builds Sources & Uses** and sizes all three debt tranches in EBITDA turns.
4. **Runs the 7-year debt schedule**: EBITDA → EBIT → interest (on beginning-of-year
   balances across all three tranches, plus a commitment fee on undrawn revolver) → net
   income → free cash flow → mandatory Term Loan amortization → **revolver draw if cash-short,
   or revolver paydown first if cash-positive** → Term Loan cash sweep → Subordinated Notes
   paydown.
5. **Computes sponsor returns at 3 candidate exit years** (Year 3, 5, and 7) from the same
   forecast, at a constant exit multiple, to isolate the MOIC-vs-IRR exit timing tradeoff.
6. **Outputs**: a deal summary, full debt schedule CSV, exit scenario comparison CSV, a debt
   paydown chart (including any revolver draw), and an exit-year MOIC/IRR comparison chart.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs** — a
mechanics demonstration rather than an analysis of a real roll-up or platform. The engine
mirrors a real multi-tranche LBO model exactly; swap in real target financials and
market-standard debt terms to make this an actual analysis.

## How to run

```bash
cd code
pip install -r requirements.txt
python lbo_model.py
```

Outputs are written to `output/`.

## Folder structure

```
full-lbo-model-business-services/
├── code/
│   ├── lbo_model.py
│   └── requirements.txt
├── data/
│   ├── lbo_assumptions.csv
│   └── forecast_drivers.csv
├── theory/
│   └── revolver_and_exit_timing.md
├── output/                  # generated summary, debt schedule, exit comparison, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Entry**: $522.5mm EV (9.5x EBITDA), financed with a **$220mm Term Loan (4.0x @ 8%)**,
  **$82.5mm Subordinated Notes (1.5x @ 11.5%)**, a **$20mm undrawn revolver**, and a
  **$230.5mm sponsor equity check**.
- The **revolver is never drawn** in the base case — free cash flow is positive every year —
  demonstrating that the facility's value is downside protection that doesn't show up in a
  healthy base case.
- The Term Loan is nearly fully repaid by Year 7 ($5.6mm remaining from $220mm), while the
  Subordinated Notes stay untouched at $82.5mm (bullet maturity, only amortized after the
  Term Loan is fully swept).
- **Exit returns show the classic MOIC-vs-IRR tradeoff**: a 3-year exit returns **1.88x MOIC
  / 23.3% IRR**, while a 7-year exit returns a much larger **3.38x MOIC but only 19.0% IRR** —
  more total dollars, at a lower annualized rate.
