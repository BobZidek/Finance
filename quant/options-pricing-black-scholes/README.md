# Black-Scholes Options Pricing Calculator with Greeks

Computes European call and put prices and their Greeks (Delta, Gamma, Vega, Theta, Rho) via
the closed-form Black-Scholes-Merton formula, verifies put-call parity holds, and charts
price/Greeks sensitivity across a range of spot prices plus a payoff diagram at expiration.

For the theory behind the formula and how to read each Greek, see
[`theory/black_scholes_theory.md`](theory/black_scholes_theory.md).

## What the code does

1. **Loads option parameters** ([`data/option_parameters.csv`](data/option_parameters.csv)) —
   spot price, strike, time to expiry, risk-free rate, volatility.
2. **Computes call and put prices** via the closed-form Black-Scholes formula.
3. **Computes all five Greeks** (Delta, Gamma, Vega, Theta, Rho) analytically for both option types.
4. **Verifies put-call parity** (`C − P = S − PV(K)`) as a correctness check independent of the
   specific Black-Scholes assumptions.
5. **Outputs**: a pricing/Greeks CSV, a summary text file with the parity check, a price-vs-spot
   chart, a 3-panel Greeks-vs-spot chart (Delta, Gamma, Vega), and a payoff diagram at expiration.

## Data note

No external data is required — Black-Scholes is a closed-form analytical formula, not a data-
driven model. Parameters in `data/option_parameters.csv` are illustrative.

## How to run

```bash
cd code
pip install -r requirements.txt
python black_scholes_model.py
```

Outputs are written to `output/`.

## Folder structure

```
options-pricing-black-scholes/
├── code/
│   ├── black_scholes_model.py
│   └── requirements.txt
├── data/
│   └── option_parameters.csv
├── theory/
│   └── black_scholes_theory.md
├── output/                  # generated pricing/Greeks table, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included parameters)

At Spot $100 / Strike $105 / 6-month expiry / 4% risk-free rate / 25% volatility:

- **Call price: $5.78** (Delta 0.47, Gamma 0.0225, Vega 0.28, Theta -$0.024/day, Rho 0.21)
- **Put price: $8.70** (Delta -0.53, Gamma 0.0225, Vega 0.28, Theta -$0.013/day, Rho -0.31)
- **Put-call parity holds to within floating-point precision** (difference on the order of
  1e-15) — strong verification that the call and put formulas are correctly implemented and
  mutually consistent.
- Gamma and Vega both **peak near the strike price**, exactly where an at-the-money option's
  value is most sensitive to both the underlying's price and its volatility.
