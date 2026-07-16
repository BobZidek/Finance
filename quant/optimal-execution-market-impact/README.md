# Optimal Execution & Market Impact — Almgren-Chriss Model

Solves for the optimal trading trajectory to liquidate a 500,000-share position over 10
periods, trading off market impact cost against timing/volatility risk (the classic
Almgren-Chriss 2000 framework), compares it against naive TWAP and immediate-liquidation
benchmarks, and traces the full execution efficient frontier across risk-aversion levels.

For the theory behind the model and how it directly parallels mean-variance portfolio
optimization, see [`theory/almgren_chriss_theory.md`](theory/almgren_chriss_theory.md).

## What the code does

1. **Loads execution parameters** ([`data/execution_parameters.csv`](data/execution_parameters.csv))
   — shares to liquidate, number of trading periods, per-period volatility, temporary and
   permanent market impact coefficients, and a base risk aversion level.
2. **Computes the closed-form Almgren-Chriss optimal trajectory** (a hyperbolic-sine curve)
   and compares it against **TWAP** (linear/equal trading each period) and **immediate
   liquidation** (everything in period one).
3. **Computes expected cost and cost standard deviation** for each strategy, quantifying the
   genuine trade-off between market impact and timing risk.
4. **Traces the full efficient frontier**: sweeps risk aversion across 5 orders of magnitude
   and shows expected cost rising smoothly as cost risk falls.
5. **Outputs**: a strategy comparison CSV, an efficient frontier CSV, a summary text file, an
   execution trajectories chart, and an efficient frontier chart.

## Data note

The asset and all execution parameters are **illustrative** — this environment couldn't reach
live market data (network/SSL restriction). The Almgren-Chriss mechanics (closed-form optimal
trajectory, cost/risk decomposition, efficient frontier) are exactly what a real trading desk
would run against calibrated real-market impact coefficients.

## How to run

```bash
cd code
pip install -r requirements.txt
python optimal_execution_model.py
```

Outputs are written to `output/`.

## Folder structure

```
optimal-execution-market-impact/
├── code/
│   ├── optimal_execution_model.py
│   └── requirements.txt
├── data/
│   └── execution_parameters.csv
├── theory/
│   └── almgren_chriss_theory.md
├── output/                  # generated strategy comparison, frontier, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Strategy | Expected Cost | Cost Std Dev (risk) |
|---|---|---|
| Almgren-Chriss Optimal | $13,850 | $116,789 |
| TWAP (naive linear) | $7,250 | $253,229 |
| Immediate Liquidation | $50,000 | $0 |

- **A genuine trade-off, not a dominance result**: TWAP has the lowest expected cost but
  highest risk; immediate liquidation has zero risk but the highest cost; the Almgren-Chriss
  optimal strategy accepts ~$6,600 more expected cost than TWAP to cut cost risk by more
  than half — the correct outcome for a risk-averse trader.
- **The efficient frontier confirms the theory exactly**: as risk aversion sweeps from
  near-zero to extreme, expected cost rises smoothly from ~$7,271 (converging to TWAP) to
  $50,000 (converging to immediate liquidation), while cost standard deviation falls
  correspondingly from ~$244,432 to ~$0 — a clean, monotonic trade-off curve.
