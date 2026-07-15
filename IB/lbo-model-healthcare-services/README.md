# LBO Model — Healthcare Services (Dental/Vet Roll-up)

A 5-year leveraged buyout of a hypothetical dental/vet roll-up platform ("BrightSmile Dental
Partners"): sources & uses, a two-tranche debt schedule with mandatory amortization and a
cash flow sweep, exit valuation, and sponsor IRR/MOIC — plus an Entry Multiple x Exit
Multiple IRR sensitivity grid.

For the theory behind each step, see [`theory/lbo_mechanics.md`](theory/lbo_mechanics.md).

## What the code does

1. **Loads deal assumptions** ([`data/lbo_assumptions.csv`](data/lbo_assumptions.csv)) — entry
   EBITDA/revenue, entry/exit multiples, debt tranche sizing (in EBITDA turns) and pricing,
   mandatory amortization %, cash sweep %, tax rate.
2. **Loads forecast drivers** ([`data/forecast_drivers.csv`](data/forecast_drivers.csv)) —
   year-by-year revenue growth, EBITDA margin, D&A%, capex%, and NWC-as-%-of-revenue (from
   which the year-over-year change in the working capital balance is derived).
3. **Builds Sources & Uses**: sizes the Term Loan and Subordinated Notes in EBITDA turns,
   plugs Sponsor Equity as the balancing figure.
4. **Runs the 5-year debt schedule**: EBITDA → EBIT → interest → net income → free cash flow
   → mandatory amortization → cash sweep (Term Loan first, then Subordinated Notes) →
   ending debt balances, with interest calculated on beginning-of-year balances each year.
5. **Computes exit returns**: Exit EV (exit multiple × final-year EBITDA) − remaining debt =
   exit equity value → MOIC and IRR.
6. **Builds an IRR sensitivity grid** across a 9.0x-11.0x Entry Multiple × 9.0x-11.0x Exit
   Multiple matrix.
7. **Outputs**: a deal summary text file, full debt schedule CSV, sensitivity grid CSV, a
   debt paydown chart, and an IRR sensitivity heatmap.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs** — a
mechanics demonstration rather than an analysis of a real roll-up platform. The engine
(Sources & Uses, waterfall debt schedule, IRR/MOIC) mirrors a real LBO model exactly; swap
in real target financials and market-standard debt terms to make this an actual analysis.

## How to run

```bash
cd code
pip install -r requirements.txt
python lbo_model.py
```

Outputs are written to `output/`.

## Folder structure

```
lbo-model-healthcare-services/
├── code/
│   ├── lbo_model.py
│   └── requirements.txt
├── data/
│   ├── lbo_assumptions.csv
│   └── forecast_drivers.csv
├── theory/
│   └── lbo_mechanics.md
├── output/                  # generated summary, debt schedule, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Entry**: $600mm EV (10.0x EBITDA), financed with **5.5x total leverage** ($330mm debt:
  4.0x Term Loan @ 8%, 1.5x Subordinated Notes @ 11%) and a **$282mm sponsor equity check**.
- Over the 5-year hold, **total debt falls from $330mm to $202.7mm** even before considering
  any EBITDA growth — pure deleveraging.
- **EBITDA grows from $60.0mm to $95.5mm** (revenue growth + 205bps of margin expansion).
- At a **flat 10.0x exit multiple**, the deal returns **2.67x MOIC / 21.7% IRR** — demonstrating
  that a well-levered, cash-generative business can hit strong PE-fund return targets without
  any multiple expansion, from deleveraging and EBITDA growth alone.
- The sensitivity grid shows IRR ranging from **13.9%** (11.0x entry / 9.0x exit) to **30.9%**
  (9.0x entry / 11.0x exit) — entry price discipline matters roughly as much as exit timing.
