# Cointegration & Pairs Trading — Theory

## Why pairs trading needs cointegration, not just correlation

Two assets can be highly *correlated* (moving together day to day) without ever being reliably
tradeable as a pair — correlation says nothing about whether the *relationship between their
price levels* is stable over time. **Cointegration** is the stronger, more useful property: two
non-stationary price series (each individually a random walk) are cointegrated if some linear
combination of them is **stationary** (mean-reverting) — meaning their spread, even though each
leg wanders unpredictably on its own, keeps returning to a stable long-run relationship. That
stationary spread is exactly what a pairs trade bets on reverting.

## The Engle-Granger two-step method

```
Step 1: Regress log(A) on log(B) via OLS  ->  log(A) = alpha + beta x log(B) + residual
         beta is the "hedge ratio" - how many units of B per unit of A keep the spread balanced
Step 2: Test the residual for stationarity (a unit root test, e.g. Augmented Dickey-Fuller)
         If the residual is stationary, A and B are cointegrated with hedge ratio beta.
```

This project constructs two price series that **are cointegrated by design** (see
`code/generate_data.py`): both share a common non-stationary trend, and their spread follows a
stationary AR(1) process — so a correctly-run test should detect the relationship.

## An important subtlety this project's results reveal

Running a standard ADF test **directly on OLS residuals** and reading off the usual Dickey-
Fuller critical values is a **known methodological trap**: those residuals come from an
*estimated* regression, not raw data, and the correct asymptotic distribution for testing
them is different (flatter-tailed) than the standard ADF distribution — using standard
critical values here tends to **over-reject the null**, making pairs look cointegrated more
often than they really are. The statistically correct approach (Engle & Granger, and later
MacKinnon) uses **adjusted critical values** specific to this two-step procedure —
implemented in `statsmodels.tsa.stattools.coint()`.

**This project's own results show the trap in action**: the naive ADF-on-residuals test gives
**p = 0.0485** (just below the 5% threshold — "looks cointegrated"), while the properly
adjusted `coint()` test gives **p = 0.142** (well above 5% — "not clearly cointegrated") — on
the *same* pair of series, constructed to genuinely be cointegrated. **The correct conclusion
is to trust `coint()`, not the naive ADF-on-residuals test** — this project deliberately keeps
both results visible (`output/pairs_trading_summary.txt`) rather than reporting only the
naive test that happens to "confirm" cointegration, since presenting only the favorable test
would be a form of test-shopping.

## Why even a properly-tested, genuinely cointegrated pair can fail to show significance

The synthetic spread's AR(1) persistence parameter (`phi = 0.96`) is **close to 1** — a
"near-unit-root" process. Statistically, near-unit-root processes are notoriously **hard to
distinguish from true unit-root (non-stationary) processes in finite samples**, because a
slowly mean-reverting series looks, over any limited observation window, very similar to one
that never reverts at all. With only 500 observations, the `coint()` test's inability to
confidently reject the null here is a **realistic illustration of test power limitations**,
not a flaw in the test or the data generation — real pairs trading research faces exactly this
challenge, and typically requires either much longer histories or restricting candidate pairs
to those with a *more clearly* fast-reverting spread before trusting a cointegration signal.

## The trading rule, and why the backtest still ran

This project's backtest proceeds using the **estimated hedge ratio regardless of the formal
significance question**, entering when the spread's z-score exceeds ±2 and exiting when it
reverts within ±0.5 — a standard, simple mean-reversion rule. The backtest produced a **1.04
Sharpe ratio and 33.75% total return over 7 trades**, which is a genuinely encouraging result
on this specific synthetic path — but given the ambiguous formal test result, a real trading
desk would treat this as a **candidate worth more data or a stricter significance bar**, not a
confirmed edge ready for capital allocation. This gap between "a promising backtest" and "a
statistically validated relationship" is one of the most important and most commonly skipped
steps in real quantitative pairs trading research.
