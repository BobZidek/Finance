# Merton Structural Credit Risk Model — Distance-to-Default

Treats each firm's equity as a call option on its (unobservable) asset value — the classic
Merton / Moody's KMV framework — solves simultaneously for implied asset value and asset
volatility from observable equity market cap and equity volatility, and computes
Distance-to-Default and implied 1-year default probability for three companies spanning
healthy to distressed.

For the theory behind the model and **its direct connection to the IB distressed debt
project**, see [`theory/merton_model_theory.md`](theory/merton_model_theory.md).

## What the code does

1. **Loads three companies' observable data** ([`data/companies.csv`](data/companies.csv)) —
   equity market cap, equity volatility, total debt, risk-free rate, and time horizon.
2. **Solves the Merton simultaneous equations** for each company's implied asset value and
   asset volatility via `scipy.optimize.fsolve`, given only observable equity data.
3. **Computes Distance-to-Default and implied 1-year default probability** using the
   risk-neutral convention.
4. **Outputs**: a comparison table CSV, a summary text file, a Distance-to-Default /
   implied-PD comparison chart, and an asset-value-vs-debt chart.

## Data note

All companies and financials are **illustrative** — a mechanics demonstration of the Merton
model. **"Anchorage Retail Holdings" deliberately reuses the exact $850mm total debt figure**
from [`IB/distressed-debt-recovery-waterfall`](../../IB/distressed-debt-recovery-waterfall)'s
post-filing capital structure — this project shows what the equity market would have been
implying about default risk **before** any bankruptcy filing, using only equity market data.

## How to run

```bash
cd code
pip install -r requirements.txt
python merton_model.py
```

Outputs are written to `output/`.

## Folder structure

```
merton-credit-risk-model/
├── code/
│   ├── merton_model.py
│   └── requirements.txt
├── data/
│   └── companies.csv
├── theory/
│   └── merton_model_theory.md
├── output/                  # generated analysis table, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Company | Distance-to-Default | Implied 1-Yr Default Probability | Asset/Debt Ratio |
|---|---|---|---|
| Sturdy Industrials (healthy) | 8.04 | ~0.00% | 4.96x |
| Balanced Manufacturing (moderate leverage) | 2.76 | 0.29% | 1.63x |
| Anchorage Retail Holdings (distressed) | **0.74** | **22.9%** | **1.01x** |

- **All three solves converged successfully**, recovering sensible implied asset values and
  asset volatilities from each company's observable equity data alone.
- **The distressed company's implied asset value barely exceeds its debt (1.01x)**, and its
  very high equity volatility (90%) — itself a market signal of distress, since equity in a
  near-the-money, highly-levered "option" is inherently volatile — combine to produce a
  genuinely alarming 22.9% one-year default probability.
- This shows exactly the kind of **early-warning signal** structural credit models are used for
  in practice: detecting elevated default risk from public equity market data, well before a
  formal restructuring process (like the one modeled in the IB project) actually begins.
