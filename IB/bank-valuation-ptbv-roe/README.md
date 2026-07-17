# Bank Valuation — Price/Tangible Book Value & ROE (Meridian Community Bancorp)

Values a hypothetical regional bank using the standard financial-institution framework —
Justified P/TBV as a function of ROE relative to Cost of Equity — computed both the simple
blended way and via a more precise sum-of-the-parts approach that separates required
regulatory capital (earning the bank's true core ROE) from excess capital (valued near book).

For the theory behind bank-specific valuation and why the excess-capital refinement matters,
see [`theory/bank_valuation_theory.md`](theory/bank_valuation_theory.md).

## What the code does

1. **Loads bank assumptions** ([`data/bank_assumptions.csv`](data/bank_assumptions.csv)) —
   tangible book value, net income, CAPM inputs, long-term growth rate, current trading
   multiple, risk-weighted assets, and required CET1 ratio.
2. **Computes Cost of Equity** via CAPM and **blended ROE** (Net Income / Total TBV).
3. **Computes the simple Justified P/TBV**: `(ROE − g) / (CoE − g)`.
4. **Computes the sum-of-parts refinement**: splits book equity into required regulatory
   capital (valued at its own, higher core ROE) and excess capital (valued at book), then sums
   the two for a more precise implied equity value.
5. **Builds a sensitivity table**: Justified P/TBV across a 5×7 ROE × Cost of Equity grid.
6. **Outputs**: a summary text file, sensitivity CSV, a valuation-comparison chart (current
   market vs. blended vs. sum-of-parts), and a sensitivity heatmap.

## Data note

The bank and all financials are **fictional/illustrative** — a mechanics demonstration of
bank valuation methodology rather than an analysis of a real institution.

## How to run

```bash
cd code
pip install -r requirements.txt
python bank_valuation_model.py
```

Outputs are written to `output/`.

## Folder structure

```
bank-valuation-ptbv-roe/
├── code/
│   ├── bank_valuation_model.py
│   └── requirements.txt
├── data/
│   └── bank_assumptions.csv
├── theory/
│   └── bank_valuation_theory.md
├── output/                  # generated summary, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Approach | ROE | Justified P/TBV | Implied Equity Value |
|---|---|---|---|
| Blended (simple) | 12.00% | 1.29x | $1,096.8mm |
| **Sum-of-Parts (core + excess)** | 14.17% (core) | 1.60x (core) | **$1,282.7mm (1.51x blended)** |

- **Cost of Equity: 9.98%** (CAPM).
- **The sum-of-parts approach implies ~17% higher equity value** than the naive blended-ROE
  approach — the bank's core operations earn a genuinely higher ROE (14.17%) once $130mm of
  non-earning excess capital is properly isolated rather than averaged into the blended figure.
- **Current market value ($892.5mm, 1.05x TBV) sits below both justified values** — the
  starting point for an investment thesis, not an automatic conclusion.
