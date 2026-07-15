# Quick LBO Returns Calculator — Consumer Products

A deliberately simplified "back of the envelope" LBO calculator for a hypothetical consumer
packaged goods company ("Meadow Brands") — the fast screening tool used before committing to
build a full multi-tranche debt model.

For the theory behind the simplification and what it approximates away, see
[`theory/quick_lbo_math.md`](theory/quick_lbo_math.md).

## What the code does

1. **Loads assumptions** ([`data/lbo_assumptions.csv`](data/lbo_assumptions.csv)) — entry
   EBITDA, entry/exit multiple, leverage multiple, blended debt rate, a flat debt-paydown
   % of EBITDA, EBITDA growth rate, hold period.
2. **Computes Entry EV, Debt, and Sponsor Equity.**
3. **Runs a simplified year-by-year schedule**: EBITDA grows at a flat rate; debt is paid
   down by a flat % of that year's EBITDA (no detailed interest/tax/capex build).
4. **Computes Exit EV, Exit Equity, MOIC, and IRR** — and, for comparison, the **unlevered**
   equivalent (same entry/exit EV, 100% equity, no debt) to isolate leverage's contribution
   to the return.
5. **Builds a quick Entry Multiple × Exit Multiple IRR sensitivity grid** (5×5).
6. **Outputs**: a summary text file, the debt paydown schedule CSV, the sensitivity grid CSV,
   an equity bridge chart, and a sensitivity heatmap.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs** — a
mechanics demonstration. The simplification (flat % of EBITDA debt paydown, no explicit
interest/tax/capex) is intentional and explained in the theory doc — see
[`PE/full-lbo-model-business-services`](../full-lbo-model-business-services) for the
detailed version that models those explicitly.

## How to run

```bash
cd code
pip install -r requirements.txt
python lbo_calculator.py
```

Outputs are written to `output/`.

## Folder structure

```
lbo-calculator-consumer-products/
├── code/
│   ├── lbo_calculator.py
│   └── requirements.txt
├── data/
│   └── lbo_assumptions.csv
├── theory/
│   └── quick_lbo_math.md
├── output/                  # generated summary, schedule, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Entry**: $340mm EV (8.5x EBITDA), $180mm debt (4.5x), **$160mm sponsor equity**.
- Over a 5-year hold, the deal returns **2.17x MOIC / 16.7% IRR** on a levered basis.
- The **unlevered equivalent returns only 1.34x MOIC / 6.0% IRR** — meaning **leverage alone
  contributes ~10.7 percentage points of IRR** in this deal, more than the underlying business
  performance itself.
- The sensitivity grid shows IRR ranging from **3.9%** (10.0x entry / 7.0x exit — paying up,
  then multiple compression) to **33.7%** (7.0x entry / 10.0x exit) — underscoring how much
  entry discipline matters relative to operational execution in this simplified framework.
