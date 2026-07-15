# Multi-Factor Investing — Theory

## The three classic factors modeled here

- **Value**: cheap stocks (measured here via earnings yield, `1/P/E` — inverted so higher
  always means "better/cheaper", consistent with the other two factors' orientation) tend to
  outperform expensive ones over time, the foundational insight behind value investing.
- **Momentum**: stocks that have performed well recently (12-month trailing return here) tend
  to keep performing well over the following months — one of the most robustly documented
  anomalies in empirical finance, despite lacking a fully agreed-upon theoretical explanation.
- **Quality**: profitable, well-run businesses (ROE here, a common quality proxy) tend to
  outperform lower-quality ones, particularly on a risk-adjusted basis.

## Standardizing before combining: the z-score step

Each factor is measured on a completely different scale (a P/E ratio, a percentage return, a
percentage ROE) — you cannot average them directly without one dominating purely because of
its units. Converting each to a **z-score** (`(value - mean) / std`) puts all three on a common
"standard deviations from the cross-sectional average" scale before combining them into a
composite score — the exact same technique used in
[`PE/deal-screening-scorecard`](../../PE/deal-screening-scorecard), applied here to public
equities instead of private acquisition targets.

## The Information Coefficient — the standard way to grade a factor

```
IC = Spearman rank correlation(Factor Score, Forward Return)
```

The IC measures how well a factor's **cross-sectional ranking** at one point in time predicts
**relative** forward returns — not whether it perfectly predicts exact returns, just whether
higher-scored stocks tend to outperform lower-scored ones. Real-world ICs for individual
factors are typically small (often 0.02-0.08 per period) but persistently positive across many
periods — a small, statistically reliable edge repeated across thousands of stock-months is
what drives real factor investing returns, not any single dramatic prediction.

## An honest note on this project's signal-to-noise ratio

This project's synthetic data was generated with a **deliberately generous signal-to-noise
ratio** (see `code/generate_data.py`'s `TRUE_WEIGHTS` and `NOISE_STD`) — strong enough that a
single 80-stock cross-section clearly recovers statistically significant, positive ICs for all
three factors (Value 0.38, Momentum 0.29, Quality 0.22, all with p-values below or near the
common 0.05 threshold). **Real single-period factor signals are almost always much weaker and
noisier than this** — this project's generous signal-to-noise ratio was chosen specifically to
make the *methodology* clearly demonstrable on a small, static dataset, not to claim these are
realistic effect sizes. A real factor research process needs **many stocks across many time
periods** (a full panel, not one snapshot) to reliably distinguish a small genuine factor
premium from noise — exactly the caveat given honest treatment in
[`VC/vc-fund-model-reserves`](../../VC/vc-fund-model-reserves)'s follow-on decisions, applied
here to a different modeling context.

## Why the Composite factor beats every individual factor

The Composite score's IC (0.51) **exceeds every individual factor's IC** (Value 0.38,
Momentum 0.29, Quality 0.22) — this isn't a coincidence, it's the same diversification logic
behind portfolio construction itself: since Value, Momentum, and Quality were generated as
**independent** (uncorrelated) signals here, combining them **averages out each one's
idiosyncratic noise while preserving their shared genuine predictive content** — mathematically
identical to why a diversified portfolio of uncorrelated assets has a better risk-adjusted
return than any single asset. Real factor combination isn't quite this clean (real factors are
correlated with each other, e.g. cheap stocks are often also lower-momentum "falling knives"),
but the core mechanism — combining imperfectly correlated *signals* reduces the noise in a
composite forecast — is genuine and is a large part of why practitioners build multi-factor
models rather than trading a single factor alone.

## Reading the quintile chart

The average forward return **rises monotonically from Q1 (-6.4%) to Q5 (+3.7%)** — exactly the
"clean staircase" pattern factor researchers look for as visual confirmation that a ranking
genuinely orders stocks by expected forward performance, not just noise that happens to
correlate. The **long-short (Q5 minus Q1) spread of 10.14%** is the return a market-neutral
strategy (long the top quintile, short the bottom) would have captured — the standard way
factor strategies are actually implemented in practice, since it isolates the factor's return
from overall market direction.
