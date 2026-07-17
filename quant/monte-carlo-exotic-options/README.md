# Monte Carlo Exotic Option Pricing — Asian & Barrier Options

Simulates risk-neutral price paths and prices a vanilla European call (validated against the
closed-form Black-Scholes price), an arithmetic-average Asian call, and an up-and-out barrier
call — the two path-dependent exotics that have no closed-form solution and require simulation.

For the theory behind Monte Carlo option pricing and why each exotic trades at a discount to
the vanilla call, see [`theory/monte_carlo_exotics_theory.md`](theory/monte_carlo_exotics_theory.md).

## What the code does

1. **Loads option parameters** ([`data/option_parameters.csv`](data/option_parameters.csv)) —
   spot, strike, time to expiry, risk-free rate, volatility, barrier level, and simulation size.
2. **Simulates 50,000 risk-neutral GBM price paths** (252 daily steps).
3. **Prices a vanilla European call via Monte Carlo** and **validates it against the
   closed-form Black-Scholes price** — the core correctness check for the whole simulation engine.
4. **Prices an Asian (arithmetic average) call** and an **up-and-out barrier call**, both
   genuinely path-dependent with no closed-form solution.
5. **Runs a convergence analysis**: re-prices the vanilla call at path counts from 500 to
   50,000, showing the Monte Carlo estimate and its confidence interval converging toward the
   closed-form price.
6. **Outputs**: a summary text file (with 95% confidence intervals for every MC estimate), a
   convergence analysis CSV, a price comparison chart, a convergence chart, and a sample-paths chart.

## Data note

Parameters are **illustrative**. The pricing mechanics (path simulation, discounting,
confidence intervals) are exactly what a production Monte Carlo option pricer would run.

## How to run

```bash
cd code
pip install -r requirements.txt
python monte_carlo_options_model.py
```

Outputs are written to `output/`.

## Folder structure

```
monte-carlo-exotic-options/
├── code/
│   ├── monte_carlo_options_model.py
│   └── requirements.txt
├── data/
│   └── option_parameters.csv
├── theory/
│   └── monte_carlo_exotics_theory.md
├── output/                  # generated summary, convergence analysis, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included parameters)

- **Validation**: Monte Carlo vanilla call price **$11.8128** vs. closed-form Black-Scholes
  **$11.8370** — the closed-form price falls comfortably within the Monte Carlo estimate's 95%
  confidence interval, confirming the simulation engine is correctly implemented.
- **Asian Call: $6.6361 — a 43.8% discount** to the vanilla call, reflecting averaging's
  reduction of effective payoff volatility.
- **Up-and-Out Barrier Call: $2.4046 — a 79.6% discount**, with a **28.7% knockout rate**
  (nearly 30% of simulated paths breach the $130 barrier and pay zero regardless of where the
  price ends up).
- **Convergence analysis confirms the standard `1/sqrt(N)` Monte Carlo error scaling**, visible
  directly in how the confidence interval narrows as path count grows from 500 to 50,000.
