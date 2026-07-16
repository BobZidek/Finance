# Merton Structural Credit Risk Model — Theory

## The core insight: equity is a call option on the firm's assets

Merton's (1974) foundational insight, later commercialized as Moody's KMV model: **a levered
firm's equity is economically equivalent to a call option on the firm's assets**, with the
debt's face value as the strike price and the debt's maturity as the option's expiry. If asset
value exceeds the debt at maturity, equity holders "exercise" — they pay off the debt and keep
the residual asset value. If asset value falls below the debt, equity holders let the option
expire worthless (default) — the firm's assets go to creditors, exactly consistent with limited
liability. This means the **same Black-Scholes machinery** used in
[`quant/options-pricing-black-scholes`](../options-pricing-black-scholes) to price a call
option can be applied directly to credit risk, treating default as the event where a call
option finishes out-of-the-money.

## The problem: asset value and asset volatility aren't observable

Unlike a normal option, where the underlying's price is directly quoted, a firm's **total
asset value and asset volatility are not directly observable** — only equity market cap and
equity volatility are. Merton's model resolves this with **two simultaneous equations**:

```
E = V x N(d1) - D x e^(-rT) x N(d2)              (equity priced as a call option on assets)
sigma_E x E = N(d1) x sigma_V x V                 (relates equity vol to asset vol via Delta)
```

where `E`, `sigma_E`, `D`, `r`, `T` are all observable, and `V` (asset value) and `sigma_V`
(asset volatility) are the two unknowns solved for **simultaneously** (via `scipy.optimize.fsolve`
here) — a firm's implied asset value and asset volatility are *inferred* from what the equity
market is doing, not measured directly.

## Distance-to-Default: the central output

```
Distance-to-Default (DD) = d2 = [ln(V/D) + (r - 0.5 x sigma_V^2) x T] / (sigma_V x sqrt(T))
Implied (risk-neutral) 1-Year Default Probability = N(-DD)
```

DD measures **how many standard deviations of asset value movement separate the firm's current
asset value from its default point (the debt level)** — a large DD means the firm would need
an enormous, many-standard-deviation asset decline to default; a DD near zero means default is
a live, near-term possibility.

## Reading this project's three-company progression

| Company | Distance-to-Default | Implied 1-Yr Default Probability | Asset/Debt Ratio |
|---|---|---|---|
| Sturdy Industrials (healthy) | 8.04 | ~0.00% | 4.96x |
| Balanced Manufacturing (moderate leverage) | 2.76 | 0.29% | 1.63x |
| Anchorage Retail Holdings (distressed) | **0.74** | **22.9%** | **1.01x** |

The healthy company's assets are worth nearly **5x** its debt with modest equity volatility —
default is a near-impossibility on this model's terms. The distressed company's implied asset
value **barely exceeds its debt (1.01x)**, and combined with very high equity volatility (90%,
itself a market signal of distress — equity in a highly-levered, near-the-money "option" is
extremely volatile), produces a genuinely alarming **22.9% one-year default probability**.

## The connection to IB/distressed-debt-recovery-waterfall — a genuinely important idea

"Anchorage Retail Holdings" in this project uses the **exact same $850mm total debt figure**
as the capital structure analyzed **after** a Chapter 11 filing in
[`IB/distressed-debt-recovery-waterfall`](../../IB/distressed-debt-recovery-waterfall). This
project asks a different, earlier question: **what was the equity market already implying about
default risk, using only publicly observable equity price and volatility, before any
bankruptcy filing occurred?** This is precisely the real-world use case for structural credit
models — equity market signals (a collapsing stock price combined with skyrocketing equity
volatility) are a leading indicator that shows up in a company's Distance-to-Default well
before a formal restructuring process begins, which is why credit analysts, distressed
investors, and risk managers monitor DD as an early-warning signal, not just a post-mortem
explanation.

## Why "risk-neutral" default probability isn't the "real-world" probability

This project computes default probability using the **risk-neutral** convention (drift = risk-
free rate `r`), consistent with the no-arbitrage option-pricing framework the whole model is
built on. **Real-world** default probability would use the firm's actual expected asset return
(typically higher than the risk-free rate, since equity/asset investors demand a risk premium)
instead of `r` in the Distance-to-Default formula — this would produce a **larger** DD and
**lower** implied default probability than the risk-neutral version reports, since real-world
expected drift is higher. The gap between risk-neutral and real-world default probability is
itself economically meaningful (it reflects the market price of credit risk), and is exactly
what separates a firm's actual credit spread from its "pure" expected-loss compensation — see
`ENHANCEMENTS.md` for extending this project to compute both.
