# Portfolio Power-Law Model — 20-Investment VC Fund

Analyzes a hypothetical 20-investment venture portfolio to quantify the power-law return
concentration central to VC portfolio construction — how much of total fund value comes from
a small number of outsized winners, versus the large fraction of investments that fail or
merely return capital.

For the theory behind why VC returns are power-law distributed and what that means for
portfolio construction, see [`theory/power_law_returns.md`](theory/power_law_returns.md).

## What the code does

1. **Loads the portfolio** ([`data/portfolio_investments.csv`](data/portfolio_investments.csv))
   — 20 hypothetical $1.5mm investments with deliberately power-law-distributed exit multiples,
   from total losses (0x) to a single "fund returner" (65x).
2. **Computes proceeds and ranks investments** by proceeds contributed (best to worst).
3. **Computes concentration statistics**: fund gross MOIC, the % of total proceeds contributed
   by the top 1/3/5 investments, and the % of deals that lost money vs. returned 5x+.
4. **Outputs**: the full ranked portfolio CSV, a summary text file, an exit-multiple bar chart
   (color-coded by outcome), a return-concentration curve (cumulative % of proceeds vs.
   cumulative % of deals), and an outcome-bucket breakdown chart.

## Data note

All 20 companies and their outcomes are **fictional/illustrative** — deliberately
hand-constructed to demonstrate a realistic power-law shape rather than modeling real
portfolio companies.

## How to run

```bash
cd code
pip install -r requirements.txt
python power_law_model.py
```

Outputs are written to `output/`.

## Folder structure

```
portfolio-power-law-model/
├── code/
│   ├── power_law_model.py
│   └── requirements.txt
├── data/
│   └── portfolio_investments.csv
├── theory/
│   └── power_law_returns.md
├── output/                  # generated ranked portfolio, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- **Fund Gross MOIC: 7.44x** ($223.2mm proceeds on $30mm invested across 20 deals).
- **The single best investment contributes 43.7% of total proceeds** — removing it alone would
  cut fund value by nearly half.
- **The top 3 investments contribute 72.6%**, and the **top 5 (just 25% of the portfolio)
  contribute 86.0%** of all proceeds.
- **40% of all investments returned below 1x** — a large loss rate that coexists comfortably
  with a strong 7.44x fund-level outcome, illustrating why individual-deal loss rates are a
  poor proxy for overall fund health in venture investing.
