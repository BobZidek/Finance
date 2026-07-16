# GARCH Volatility Forecasting — Theory

## Why volatility isn't constant — and why that matters

Every model elsewhere in this repo that uses "volatility" (Black-Scholes, the mean-variance
optimizer, VaR/CVaR) treats it as a **single fixed number** — the historical standard
deviation. Real markets don't behave this way: volatility **clusters** — a large move today
makes a large move tomorrow more likely, and a calm period tends to stay calm — a well-
documented empirical fact (visible in this project's own generated data: see
`output/volatility_comparison.png`, where the true volatility path shows genuine sustained
high- and low-volatility regimes, not random day-to-day noise). GARCH (Generalized
AutoRegressive Conditional Heteroskedasticity) models this clustering directly, rather than
assuming it away.

## The GARCH(1,1) model

```
sigma^2_t = omega + alpha x epsilon^2_(t-1) + beta x sigma^2_(t-1)
```

Today's variance (`sigma^2_t`) depends on: a baseline level (`omega`), yesterday's squared
return shock (`alpha x epsilon^2_(t-1)` — how much a *recent surprise* moves volatility), and
yesterday's variance itself (`beta x sigma^2_(t-1)` — how much volatility *persists*). This
project generated synthetic data from a **known** GARCH(1,1) process (alpha=0.09, beta=0.88)
specifically so the fitted model's recovered parameters can be checked against ground truth —
and they come out close (fitted alpha=0.095, beta=0.833), a genuine verification that the
`arch` library's maximum-likelihood fitting procedure is working correctly on this data.

## Persistence, and why it matters for forecasting

```
Persistence = alpha + beta
```

This project's persistence is **0.93 (fitted) vs. 0.97 (true)** — both close to 1.0, which is
typical for real daily equity/asset returns. **High persistence means volatility shocks decay
slowly** — a spike in volatility today is expected to remain elevated for many days or weeks,
not revert immediately. This directly shapes the shape of the forward volatility forecast
(`output/volatility_forecast.png`): rather than jumping straight to the long-run average, the
forecast decays gradually from the current conditional volatility level toward the long-run
unconditional level, at a rate governed by persistence.

## Comparing three volatility estimation approaches

| Method | What it does |
|---|---|
| **Constant (unconditional) volatility** | The full-sample standard deviation — one number, never updates |
| **Rolling window volatility** | Standard deviation of the last 20 days — updates, but weights all 20 days equally and drops old information abruptly at the window edge |
| **GARCH(1,1) conditional volatility** | Explicitly models how yesterday's shock and yesterday's variance combine to predict today's variance — updates every day, with a principled (not ad hoc) weighting of recent vs. historical information |

This project evaluates all three by checking how well each day's volatility *estimate*
correlates with the **next day's realized |return|** (a standard, simple proxy for
next-day realized volatility). **Both GARCH (correlation 0.226) and rolling volatility
(0.202) meaningfully outperform constant volatility (correlation ~0.000, by construction,
since a single fixed number can't correlate with anything that varies)** — confirming that
*some* form of time-varying volatility estimate is essential, with GARCH showing a modest edge
over the simpler rolling-window approach in this specific comparison.

## Why this connects directly to the VaR/CVaR project

[`quant/risk-model-var-cvar`](../risk-model-var-cvar) demonstrated that assuming a **normal
return distribution** understates tail risk when real returns are fat-tailed. GARCH addresses a
**related but distinct** problem: even within a normal-distribution assumption, using a single
**constant volatility** for VaR (rather than the current, conditionally elevated or depressed
volatility) can badly mis-time risk — a VaR estimate computed during a genuinely calm period
using a long historical average will understate risk once volatility clusters upward, and vice
versa. A production risk system typically combines both fixes: a GARCH-based conditional
volatility estimate **and** a fat-tailed (not normal) distributional assumption, addressing two
separate, complementary failure modes of the simplest parametric VaR approach.
