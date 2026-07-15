# Full Systematic Strategy — Theory

## The four pieces of a real systematic strategy, combined

Earlier quant projects in this repo each build one piece of a systematic trading strategy in
isolation. This capstone combines all four into one working pipeline:

1. **Signal generation** — the Value/Momentum/Quality composite scoring from
   [`quant/multi-factor-stock-ranking`](../multi-factor-stock-ranking), extended here into a
   genuine **36-month panel** (that project's own flagged limitation — a single snapshot — is
   exactly what this project fixes).
2. **Portfolio construction** — equal-weighted, dollar-neutral long top-quintile / short
   bottom-quintile positions each month, rebuilt from scratch every rebalance.
3. **Risk management** — monthly **volatility targeting**: scale gross exposure up or down so
   the strategy's realized volatility tracks a target level (8% annualized here), using a
   trailing 6-month realized volatility estimate, capped at 2x leverage to avoid over-scaling
   during unusually calm periods.
4. **Backtesting with transaction costs and performance attribution** — turnover-based costs
   applied every rebalance, and a regression of net strategy returns on each factor's own
   return to decompose *where* the strategy's performance actually came from.

## Why an early version of this project had to be recalibrated

The first version of this project reused signal strength assumptions directly from the
single-stock cross-sectional ranking project — and produced a **Sharpe ratio above 9 and zero
max drawdown across 36 months**, an obviously unrealistic result (real systematic strategies
essentially never sustain Sharpe ratios above 2-3, and a strategy with literally zero monthly
losses over 3 years is a red flag, not a good sign). The cause: **a long/short quintile
portfolio averages returns across ~8 stocks per leg**, which mechanically **reduces
portfolio-level noise** relative to any single stock's noise (the same diversification
mathematic behind portfolio theory itself) — so a signal strength that produces a *believable*
individual-stock Information Coefficient becomes wildly amplified once averaged into a
portfolio return. The signal weights were reduced roughly 7x to produce believable portfolio-
level results — a concrete illustration of why **calibrating a signal's strength requires
accounting for how it will actually be portfolio-constructed**, not just how it performs at the
individual-security level.

## Volatility targeting — why risk management isn't just "how big is my bet"

```
Vol Scalar_t = Target Monthly Vol / Trailing Realized Volatility (last 6 months)
Position Size_t = Base Position x Vol Scalar_t   (capped at 2x leverage)
```

Without vol targeting, a strategy's realized risk drifts with market conditions — the same
nominal position size produces very different actual risk depending on how volatile the
underlying signal has recently been. Scaling exposure inversely with trailing volatility keeps
realized risk closer to a stated target over time, and is standard practice at systematic
funds — not primarily to boost returns, but to make the strategy's risk **predictable and
comparable** across different market regimes, which matters enormously for position sizing at
the fund level and for meeting a mandate's stated risk budget.

## Why transaction costs matter here, concretely

This project's backtest shows **gross (before-cost) Sharpe of 1.07 falling to net Sharpe of
0.75** after applying a 15bps-per-unit-turnover cost — cumulative transaction costs consumed
**8.45 percentage points** of total return over the 3-year backtest. Monthly rebalancing with
full quintile reconstruction generates substantial turnover (every stock that crosses a
quintile boundary changes the portfolio), and this project deliberately reports both gross and
net figures side by side — a strategy that looks attractive gross but marginal net is a common
and important real-world finding, not something to gloss over by only reporting the flattering number.

## Reading the performance attribution

```
Net Return_t = alpha + beta_Value x ValueFactorReturn_t + beta_Momentum x MomentumFactorReturn_t
               + beta_Quality x QualityFactorReturn_t + residual_t
```

This regression decomposes the strategy's actual realized returns into how much came from each
underlying factor's own performance that month. In this project's run, **all three factor
betas are positive and statistically significant** (Value 0.29, Momentum 0.44, Quality 0.58,
all with p-values well below 0.05), with an **R² of 0.756** — meaning about three-quarters of
the strategy's return variance is explained by exposure to the three named factors, and roughly
a quarter comes from residual/idiosyncratic sources (stock selection *within* the factor
framework, noise, or genuine skill beyond simple factor exposure — a real backtest can't
distinguish those without further analysis). This is exactly the kind of attribution a real
systematic fund reports to investors: not just "we made X%," but "here's precisely which
factors drove it, and how much is left unexplained."
