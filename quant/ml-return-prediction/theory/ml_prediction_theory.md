# ML Return Prediction — Theory

## The pipeline, and where look-ahead bias sneaks in

1. **Feature engineering**: momentum (5-day, 20-day), realized volatility (20-day rolling),
   and a mean-reversion signal (% deviation from the 20-day moving average) — all computed
   using only information available **as of today's close**.
2. **Target**: **tomorrow's** return (`shift(-1)`), so the model is genuinely predicting the
   future, not describing the past.
3. **Time-ordered train/test split** (70%/30%, no shuffling): this is not optional. Shuffling
   before splitting — standard practice for most ML problems — would let the model train on
   data from *after* some of its test observations, silently leaking future information into
   training and producing a backtest that looks far better than any real trading strategy
   could achieve. Financial time series **must** be split chronologically.

## A real bug this project's own development process caught

An earlier version of this project's mean-reversion feature computed
`(Close − SMA_20) / rolling_std(daily_returns, 20)` — dividing a **price-level** quantity by a
**return-level** volatility estimate, a unit mismatch that produced a badly-scaled, uninformative
feature (returns have units of ~1%, prices have units of ~$100, so dividing one by the other
produces numbers on the wrong scale entirely). Fixing it to `(Close − SMA_20) / SMA_20` (a
proper percentage deviation, matching how the signal was actually generated in
`generate_data.py`) is documented here specifically because **catching this kind of unit
mismatch is a routine, essential part of building any quantitative feature pipeline** — it's
mentioned explicitly rather than silently fixed and forgotten, since a reader benefits more
from seeing the debugging process than from a spotless-looking final result.

## The honest finding: even a known, injected signal is hard to recover reliably here

This project's synthetic data was generated with a **known, injected relationship** between
next-day return and each stock's own prior momentum/mean-reversion signals (see
`generate_data.py`) — deliberately set at a generous strength, since real single-asset
next-day return predictability is far weaker still. Even so, the out-of-sample results are
modest and mixed:

| Model | Directional Accuracy | Information Coefficient |
|---|---|---|
| Ridge | 50.0% (= coin flip) | 0.033 (weak positive) |
| Random Forest | 51.3% | 0.003 (essentially zero) |

And the resulting sign-based backtest **loses money for both models**, even before
transaction costs (Ridge: -19.3% gross total return over the test period; Random Forest:
-15.8% gross), while buy-and-hold gained +76.1% over the same period. **This is a genuine,
useful finding, not a failed experiment to be hidden**: it demonstrates that (1) a positive but
small Information Coefficient does not reliably translate into a profitable simple sign-based
trading rule, and (2) predicting a **single asset's own next-day return from its own recent
technical history** is a fundamentally harder statistical problem than it might appear —
consistent with decades of empirical finance research showing weak-form market efficiency
roughly holds for simple technical signals at daily frequency.

## Why this contrasts sharply with the cross-sectional factor model project

[`quant/multi-factor-stock-ranking`](../multi-factor-stock-ranking) cleanly recovered strong,
statistically significant Information Coefficients (0.22-0.51) from a similarly-scaled
injected signal. The key structural difference: that project ranks **80 independent stocks at
a single point in time** (a cross-section), while this project predicts **one stock's own
returns across time** (a time series). Averaging a noisy signal across 80 *independent*
observations reduces noise dramatically (a form of diversification, exactly as in portfolio
theory); a single asset's own price history is **one long, highly autocorrelated path** with
no comparable averaging effect available — each day's "observation" is not independent of the
last. This is a large part of **why real quantitative equity strategies emphasize
cross-sectional ranking and portfolio construction across many names, rather than trying to
time a single asset's own next-day moves** — this project's contrasting result with the factor
model project demonstrates that structural lesson empirically, not just as an assertion.

## What would need to change to get a genuinely profitable signal here

A real quant research process facing this result would **not** conclude "the signal doesn't
exist" — it would conclude the **current approach can't reliably extract it from a single
noisy series with this feature set and sample size**, and would investigate: more data (many
more years, or many correlated assets pooled together), better features, ensemble/regularization
tuning, or — most realistically — accepting that **daily single-asset return prediction from
simple technical features genuinely doesn't offer a robust edge**, and redirecting research
toward cross-sectional, longer-horizon, or fundamentally different signal sources instead
(see `ENHANCEMENTS.md`).
