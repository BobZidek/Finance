# Mean-Variance Portfolio Optimizer — Efficient Frontier

Builds the Markowitz efficient frontier for an 8-asset-class universe (US/international/EM
equities, investment-grade and high-yield bonds, REITs, commodities), identifies the Global
Minimum Variance and Maximum Sharpe Ratio (tangency) portfolios, and plots the Capital Market
Line.

For the theory behind mean-variance optimization and why several assets get 0% weight, see
[`theory/mean_variance_optimization.md`](theory/mean_variance_optimization.md).

## What the code does

1. **Loads asset assumptions** ([`data/asset_assumptions.csv`](data/asset_assumptions.csv))
   — expected return and volatility for 8 asset classes — and a hand-built **correlation
   matrix** ([`data/correlation_matrix.csv`](data/correlation_matrix.csv)).
2. **Builds the covariance matrix**, with a defensive eigenvalue-clipping check that corrects
   the correlation matrix if it isn't positive semi-definite (a common risk with hand-built
   correlation matrices).
3. **Builds the efficient frontier**: for 40 target return levels, solves a constrained
   quadratic optimization (via `scipy.optimize.minimize`, long-only) for the minimum-variance
   portfolio achieving that return.
4. **Identifies the Global Minimum Variance portfolio** and the **Maximum Sharpe Ratio
   (tangency) portfolio** via separate optimizations.
5. **Outputs**: the efficient frontier CSV, portfolio weights CSV, a summary text file, a
   frontier chart (with individual assets, GMV, tangency portfolio, and the Capital Market
   Line all plotted), and a GMV-vs-tangency weight comparison chart.

## Data note

Expected returns, volatilities, and the correlation matrix are **illustrative, hand-set
assumptions** — this environment couldn't reach live market data (network/SSL restriction).
The optimization mechanics are exactly what you'd run against real historical return statistics.

## How to run

```bash
cd code
pip install -r requirements.txt
python optimizer_model.py
```

Outputs are written to `output/`.

## Folder structure

```
portfolio-optimizer-efficient-frontier/
├── code/
│   ├── optimizer_model.py
│   └── requirements.txt
├── data/
│   ├── asset_assumptions.csv
│   └── correlation_matrix.csv
├── theory/
│   └── mean_variance_optimization.md
├── output/                  # generated frontier, weights, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Global Minimum Variance**: 5.06% expected return, 5.41% volatility, 0.20 Sharpe —
  dominated by US Investment Grade Bonds (82.7% weight).
- **Maximum Sharpe (Tangency)**: 7.63% expected return, 10.21% volatility, **0.36 Sharpe** —
  the best risk-adjusted portfolio in this universe, mixing US equities, bonds, and high yield.
- **International Developed Equity, Emerging Markets Equity, and REITs all receive 0% weight**
  in both optimal portfolios — a textbook "corner solution" outcome from mean-variance
  optimization, explained in the theory doc rather than treated as an error.
