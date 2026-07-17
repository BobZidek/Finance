# Kelly Criterion — Optimal Position Sizing & Risk of Ruin

Computes the Kelly-optimal bet fraction for a repeated favorable binary bet (55% win
probability, 1:1 payoff), derives the analytical growth-rate curve, and runs a 2,000-path
Monte Carlo simulation comparing Half Kelly, Full Kelly, 2x Kelly, and a reckless 4x Kelly
fraction — demonstrating that overbetting relative to the Kelly fraction can produce negative
long-run growth despite every individual bet having positive expected value.

For the theory behind the Kelly formula and why it maximizes geometric, not arithmetic,
growth, see [`theory/kelly_criterion_theory.md`](theory/kelly_criterion_theory.md).

## What the code does

1. **Loads bet assumptions** ([`data/bet_assumptions.csv`](data/bet_assumptions.csv)) — win
   probability, payoff ratio, number of bets per path, and number of simulated paths.
2. **Computes the Kelly-optimal fraction** and the **analytical growth-rate curve** as a
   function of bet fraction.
3. **Runs Monte Carlo simulations** (2,000 independent paths of 500 sequential bets each) at
   four bet fractions: Half Kelly, Full Kelly, 2x Kelly, and a reckless 4x Kelly.
4. **Computes summary statistics** per strategy: median/mean terminal wealth, average and worst
   max drawdown, and risk of ruin (probability terminal wealth falls below 5% of starting wealth).
5. **Outputs**: a strategy comparison CSV, a summary text file, an analytical growth-rate
   curve chart, a 4-panel sample-paths chart, and a strategy comparison chart.

## Data note

The bet structure is **illustrative** — a mechanics demonstration of Kelly sizing rather than
a real gambling or trading strategy. The mathematics apply identically to any repeated
favorable-edge situation, including position sizing in trading strategies.

## How to run

```bash
cd code
pip install -r requirements.txt
python kelly_model.py
```

Outputs are written to `output/`.

## Folder structure

```
kelly-criterion-position-sizing/
├── code/
│   ├── kelly_model.py
│   └── requirements.txt
├── data/
│   └── bet_assumptions.csv
├── theory/
│   └── kelly_criterion_theory.md
├── output/                  # generated comparison, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Strategy | Bet Fraction | Growth Rate | Median Terminal Wealth | Risk of Ruin |
|---|---|---|---|---|
| Half Kelly | 5.0% | +0.00375 | 7.22x | 0.0% |
| **Full Kelly** | **10.0%** | **+0.00501 (highest)** | **12.23x (highest)** | 0.6% |
| 2x Kelly (overbet) | 20.0% | **-0.00014 (negative)** | **0.93x (below start!)** | 25.6% |
| Reckless (4x Kelly) | 40.0% | -0.04481 | ~0 | 98.2% |

- **Full Kelly maximizes both the analytical growth rate and the empirical median terminal
  wealth** — confirmed by Monte Carlo, not just theory.
- **2x Kelly — just double the theoretically optimal fraction — produces a negative growth
  rate**, meaning the *typical* outcome after 500 bets is to end up with *less* wealth than you
  started with, despite every individual bet still carrying a genuine positive edge.
- **Half Kelly sacrifices ~25% of the growth rate for a materially smoother ride** (0% risk of
  ruin vs. 0.6% at Full Kelly) — the real reason many practitioners deliberately bet below the
  theoretical optimum.
