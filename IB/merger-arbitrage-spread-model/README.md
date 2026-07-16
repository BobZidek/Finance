# Merger Arbitrage Spread Model — Vantage Pharma Solutions

Analyzes a hypothetical pending all-cash acquisition from a merger-arbitrage perspective:
gross and annualized spread, the market-implied probability of deal completion backed out
from the current trading price, an analyst's independently-assumed completion probability and
resulting expected return, and the strategy's characteristic asymmetric risk/reward profile.

For the theory behind merger arbitrage and how to interpret market-implied deal probability,
see [`theory/merger_arbitrage_theory.md`](theory/merger_arbitrage_theory.md).

## What the code does

1. **Loads deal assumptions** ([`data/deal_assumptions.csv`](data/deal_assumptions.csv)) —
   pre-announcement price, deal price, current trading price, downside price if the deal
   breaks, days to close, and an analyst's own assumed probability of close.
2. **Computes gross and annualized spread**, and the **market-implied probability of deal
   completion** (solved from the current price, deal price, and downside price).
3. **Computes the analyst's expected return** under their own independently-assumed
   completion probability, and compares it against the market-implied assumption.
4. **Builds a probability sensitivity table**: expected return across a range of assumed
   completion probabilities, marking both the market-implied and analyst-assumed points.
5. **Outputs**: a summary text file, a probability sensitivity CSV, a probability-sensitivity
   chart, and an asymmetric risk/reward bar chart.

## Data note

The target, acquirer, and all deal terms are **fictional/illustrative** — a mechanics
demonstration of merger arbitrage analysis rather than an analysis of a real pending deal.

## How to run

```bash
cd code
pip install -r requirements.txt
python merger_arb_model.py
```

Outputs are written to `output/`.

## Folder structure

```
merger-arbitrage-spread-model/
├── code/
│   ├── merger_arb_model.py
│   └── requirements.txt
├── data/
│   └── deal_assumptions.csv
├── theory/
│   └── merger_arbitrage_theory.md
├── output/                  # generated summary, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Gross spread: $2.50 (5.05%)**, annualizing to **10.1%** if the deal is assumed certain to close.
- **Market-implied probability of close: 79.17%** — extracted directly from the current
  trading price, deal price, and downside price if the deal breaks.
- At the **analyst's own 90% assumed probability** (more bullish than the market), **expected
  return to close is +2.63% (5.25% annualized)** — a real edge relative to the market's
  implied view, but far smaller than the naive certain-close spread.
- **Asymmetric risk profile**: only **+5.05% upside if the deal closes**, against
  **-19.19% downside if it breaks** — the defining structural feature of merger arbitrage
  returns.
