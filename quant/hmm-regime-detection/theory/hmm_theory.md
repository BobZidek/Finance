# Hidden Markov Model Regime Detection — Theory

## What a regime-switching model captures that GARCH doesn't

[`quant/garch-volatility-forecasting`](../garch-volatility-forecasting) models volatility as
continuously evolving based on recent shocks. A **Hidden Markov Model (HMM)** captures a
different, complementary idea: markets sometimes behave as if they're switching between a small
number of **discrete regimes** (e.g., "calm bull market" vs. "turbulent bear market"), each with
its own characteristic mean return and volatility, with **persistence** — once in a regime,
markets tend to stay there for a while rather than switching every day. The "hidden" part means
the regime itself is never directly observed — only the returns it produces — and the model's
job is to infer which regime was most likely in effect at each point in time, purely from the
statistical pattern of the observed returns.

## The two hidden states, and how they were designed to be genuinely persistent

This project's synthetic data alternates between:
- **Calm**: mean daily return +0.06%, daily volatility 0.8% — a low-vol, modestly positive regime.
- **Turbulent**: mean daily return −0.10%, daily volatility 2.5% — a much more volatile, negative regime.

The **transition matrix** (98% chance of staying Calm each day, 95% chance of staying
Turbulent) is what makes this a genuine *regime-switching* process rather than random daily
noise — regimes here typically persist for **weeks to months** at a time (a 98% daily
persistence implies an average Calm regime length of `1/(1-0.98) = 50` trading days), matching
how real market regimes are believed to behave.

## Fitting via Baum-Welch, decoding via Viterbi

The `hmmlearn` library fits the model's parameters (state means, variances, and the transition
matrix) via the **Baum-Welch algorithm** (an Expectation-Maximization procedure specific to
HMMs), then infers the most likely regime at each point in time via the **Viterbi algorithm** —
distinct from simply classifying each day independently, since Viterbi accounts for the
transition probabilities too (a single day's return looking "turbulent" isn't enough to flip
the decoded regime if the surrounding days strongly suggest a calm regime is still in effect).

**A note on convergence**: this project's fit produces a "model is not converging" warning from
`hmmlearn` — a small numerical wobble (log-likelihood decreasing by less than 0.01 between the
final two EM iterations) common with Baum-Welch near a local optimum, not a sign the fit failed.
The recovered parameters and 97.2% decoding accuracy (reported below) confirm the fit is
practically sound despite the warning — worth noting explicitly since silently ignoring solver
warnings, or silently suppressing them, would be poor practice.

## Reading this project's results

| State | Fitted Mean (true) | Fitted Std (true) |
|---|---|---|
| Calm | 0.00103 (0.00060) | 0.00834 (0.00800) |
| Turbulent | -0.00044 (-0.00100) | 0.02591 (0.02500) |

The fitted volatilities are close to the true generating values; the fitted **means** show more
estimation noise (particularly for Turbulent, which — at only ~23.7% of the 1,500-day sample —
has a smaller effective sample to estimate from). This is expected and realistic: **mean
returns are always much harder to estimate precisely than volatility**, from a statistical
standpoint, regardless of the model — a well-known and important limitation to state plainly
rather than imply the fit is more precise than it actually is.

**Regime decoding accuracy: 97.2%** against the known true regime labels — a strong result,
confirming the HMM genuinely recovers the underlying regime structure from return data alone,
not just fitting noise.

## An important, honest limitation: this backtest is in-sample

The regime-aware strategy shown here (`output/regime_aware_backtest.png`, cutting exposure to
50% whenever the *decoded* regime is Turbulent) uses regimes decoded from a model **fit on the
entire dataset at once** — meaning the model implicitly had access to the full historical
return series, including data from *after* any given day, when it decoded that day's regime.
**This is not a legitimate out-of-sample backtest** — a real trading strategy could only use
regime estimates built from data available *up to that point in time*. The strong-looking
result (Sharpe 1.04 vs. 0.60 for buy-and-hold, max drawdown -19.0% vs. -37.5%) should be read
as a demonstration that the *decoded regimes correlate strongly with genuinely different return
environments* — not as evidence that a live, causally-correct regime-detection trading strategy
would perform this well. See `ENHANCEMENTS.md` for how to build the walk-forward version that
would actually test this fairly.
