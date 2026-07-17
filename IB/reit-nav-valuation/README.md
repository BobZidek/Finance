# REIT Net Asset Value (NAV) Valuation — Coastal Retail Properties Trust

Values a hypothetical shopping center REIT via the standard real estate methodology — market
cap rates applied by property type to derive property-level value, netted against debt and
preferred equity for NAV per share — and cross-checks against a P/FFO multiple approach.

For the theory behind cap-rate-driven NAV valuation and FFO, see
[`theory/reit_nav_theory.md`](theory/reit_nav_theory.md).

## What the code does

1. **Loads the property portfolio** ([`data/property_portfolio.csv`](data/property_portfolio.csv))
   — NOI and market cap rate for 3 property types (Grocery-Anchored, Power Centers, Mixed-Use).
2. **Loads balance sheet assumptions** ([`data/balance_sheet_assumptions.csv`](data/balance_sheet_assumptions.csv))
   — cash, other investments, debt, preferred equity, share count, current stock price, and
   FFO inputs.
3. **Computes NAV**: each property valued at NOI ÷ its own cap rate, summed and netted against
   debt/preferred equity for NAV per share.
4. **Computes FFO and a P/FFO cross-check**: FFO = Net Income + Real Estate D&A, compared
   against a peer P/FFO multiple for an independent implied value.
5. **Builds a cap rate sensitivity table**: NAV per share across a ±100bp shift applied
   uniformly to all property types.
6. **Outputs**: property valuations CSV, cap rate sensitivity CSV, a summary text file, a
   NAV bridge waterfall chart, and a cap rate sensitivity chart.

## Data note

The REIT and all property/financial data are **fictional/illustrative** — a mechanics
demonstration of REIT NAV valuation rather than an analysis of a real portfolio.

## How to run

```bash
cd code
pip install -r requirements.txt
python reit_nav_model.py
```

Outputs are written to `output/`.

## Folder structure

```
reit-nav-valuation/
├── code/
│   ├── reit_nav_model.py
│   └── requirements.txt
├── data/
│   ├── property_portfolio.csv
│   └── balance_sheet_assumptions.csv
├── theory/
│   └── reit_nav_theory.md
├── output/                  # generated property valuations, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **NAV per Share: $14.52** ($2,404.4mm total real estate value across 3 property types, less
  $1,050mm debt and $75mm preferred equity).
- **FFO per Share: $1.26**; at the peer 12.5x P/FFO multiple, an **independently-implied value
  of $15.79/share**.
- **Both approaches agree directionally**: the current $12.80 stock price trades at an
  **11.8% discount to NAV** and an even wider **18.9% discount to the P/FFO-implied value** —
  two independent methods pointing the same direction, a stronger signal than either alone.
- **Grocery-Anchored Centers command the lowest cap rate (6.25%)** and therefore the highest
  value per dollar of NOI, reflecting their defensive tenant base — exactly the pattern real
  cap-rate-driven valuation would predict.
