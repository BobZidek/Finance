# Moving-Average Crossover Strategy — Theory

## The strategy

A **golden cross / death cross** trend-following strategy: go long when a short-term moving
average (50-day) rises above a long-term moving average (200-day) — interpreted as the trend
turning bullish — and go flat (to cash) when it crosses back below. It's one of the oldest and
most widely known systematic trading rules, valued for its simplicity and interpretability
rather than for being state-of-the-art.

```
Signal_t = 1 if SMA(50)_t > SMA(200)_t, else 0
Position_t = Signal_(t-1)     <- trade on the NEXT day's return, avoiding look-ahead bias
```

**Avoiding look-ahead bias matters mechanically, not just philosophically**: today's signal
is only known at today's close, so the earliest you can actually act on it is tomorrow's open.
Backtests that apply today's signal to today's return are silently cheating — this project's
`Position` is explicitly the *prior* day's signal, shifted forward one day.

## Why this project's result is an honest, useful outcome — not a failure

The strategy **underperformed buy-and-hold in total return (12.5% vs. 25.0%) and in every
single regime tested**, including the strong uptrend regime where it actually lost money
(-2.7%) while buy-and-hold gained 4.3%. This is a real, common, and important result to
understand rather than something to hide or "fix" by cherry-picking a friendlier backtest
period:

1. **The 200-day SMA needs 200 days of data before it can generate a signal at all.** With
   only 3 years (756 days) of data, the strategy is **structurally unable to take any position
   for the first ~200 trading days** — which, in this project's synthetic data, falls entirely
   within the first "Uptrend" regime. The strategy simply couldn't participate in a meaningful
   chunk of the best-performing period, independent of whether the *rule itself* was good.
2. **Only 3 trades occurred across the whole 3-year backtest.** A strategy with this few
   trades has a very small sample size — its performance in this specific backtest reveals
   relatively little about how the *rule* would perform on average across many market
   histories. This is exactly why single-path backtests (this project included) should be read
   as illustrative, not as proof a strategy "works" or "doesn't work" — see `ENHANCEMENTS.md`
   for how to test across many simulated price paths instead of one.
3. **Trend-following strategies are known to lag at trend inflection points by construction**
   — a moving average, by definition, only detects a new trend after enough new data has
   accumulated to move the average, meaning the strategy always enters late and exits late
   relative to the trend's true starting/ending point. This is a real, permanent structural
   cost of the approach, not a bug in this specific implementation.

## What a fair evaluation of a trend-following rule requires

- **Multiple independent market histories** (or many historical periods), not one, since any
  single backtest period can happen to favor or disfavor the rule by chance.
- **A warmup-aware evaluation window** — comparing strategy vs. buy-and-hold performance only
  from the point the strategy first has a valid signal, not from day 1, isolates the "is the
  rule good" question from the "how much data does this rule need before it can act" question.
- **Transaction cost sensitivity** — with only 3 trades here, costs barely matter; a
  faster-trading variant (shorter windows) would need real transaction cost assumptions
  (see [`quant/ml-return-prediction`](../ml-return-prediction) for where those are modeled).

## Sharpe ratio and drawdown, read correctly

```
Sharpe = (Annualized Return - Risk-Free Rate) / Annualized Volatility
```

The strategy's lower volatility (14.99% vs. 18.65% for buy-and-hold) reflects real risk
reduction from being in cash during the flat/negative crossover periods — but its **much lower
Sharpe (0.07 vs. 0.28)** shows that risk reduction wasn't compensated by proportionally
preserved return in this particular backtest. Max drawdown was only modestly better
(-21.1% vs. -22.9%) — the strategy didn't meaningfully protect against the deepest single
decline either, since that decline likely happened while the strategy was still in a long
position (crossovers lag drawdown starts too).
