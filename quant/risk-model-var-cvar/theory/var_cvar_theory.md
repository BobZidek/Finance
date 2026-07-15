# VaR, CVaR, and the Cost of Assuming Normality — Theory

## What VaR and CVaR measure

```
VaR (Value at Risk) at confidence level c: the loss that will NOT be exceeded with
    probability c over a given horizon (e.g., "95% 1-day VaR of $92,338" means there's
    only a 5% chance of losing more than $92,338 in a single day).

CVaR (Conditional VaR / Expected Shortfall): the AVERAGE loss, GIVEN that the loss
    exceeds VaR - i.e., "if we do breach VaR, how bad does it typically get?"
```

CVaR is the more informative risk measure of the two, because VaR says nothing about the
*severity* of losses beyond the threshold — two portfolios can have identical VaR while one
has a far worse tail beyond it. This project computes both, via three different methods.

## The three methods

1. **Historical Simulation**: take the actual empirical distribution of past portfolio
   returns and read off the relevant percentile directly. Makes **no distributional
   assumption** — its accuracy depends entirely on whether the historical sample is
   representative of future risk.
2. **Parametric (Variance-Covariance)**: assume portfolio returns are **normally
   distributed**, estimate the mean and standard deviation from history, and compute VaR/CVaR
   from the normal distribution's closed-form formulas. Fast and simple — but only as good as
   the normality assumption.
3. **Monte Carlo Simulation**: simulate a large number of possible future portfolio outcomes
   from an assumed *asset-level* return-generating model, then read off the percentile of the
   simulated distribution. This project deliberately simulates from a **correctly-specified
   multivariate Student-t distribution** (matching the actual fat-tailed process the
   underlying data was generated from) rather than a normal one — the whole point of this
   project is to show what happens when your assumed model matches vs. doesn't match reality.

## The central finding: normality understates tail risk

At **99% confidence**, this project's three methods diverge sharply:

| Method | 99% 1-Day VaR | Backtested Exceedances (expected: 7.56) |
|---|---|---|
| Historical | $159,292 | 8 |
| Parametric (Normal) | $126,350 | **14** |
| Monte Carlo (Student-t) | $143,836 | 11 |

**Parametric (Normal) VaR understates the historical result by ~21% ($33K)** — and the
backtest makes the consequence concrete: a risk model that assumes normality would have been
**breached nearly twice as often as its own 99% confidence level implies** (14 actual
exceedances vs. 7.56 expected). A trading desk or risk manager relying on the normal
assumption here would be **systematically undercapitalized against tail risk**, discovering
the gap only when a genuinely large loss occurs — exactly the failure mode "VaR models" were
criticized for during real market stress events, where realized losses repeatedly exceeded
what normal-distribution VaR implied should be a rare event.

**Monte Carlo (Student-t), using the correctly-specified fat-tailed model, tracks the
historical result far more closely** (11 exceedances vs. 8 actual, vs. parametric's 14) —
demonstrating that the problem isn't with parametric/simulation-based VaR *in general*, but
specifically with the **normal distribution assumption** when real returns have fatter tails
than normal (as most real asset returns genuinely do — large market moves happen more often
than a normal distribution predicts, a well-documented empirical fact, not just a modeling
choice made for this project).

## Why the gap is smaller at 95% than at 99%

At 95% confidence, the three methods' VaR estimates are much closer together than at 99%. This
is expected: **fat tails matter more the deeper into the tail you look**. The 95th percentile
sits closer to the "body" of the distribution, where normal and fat-tailed distributions look
fairly similar; the 99th percentile sits further into the tail, exactly where a fat-tailed
distribution diverges most from a normal one. This is a genuinely important practical lesson:
**the choice of distributional assumption matters far more for extreme-confidence risk
measures than for moderate ones** — a risk model that looks "fine" at 95% VaR can still be
dangerously wrong at 99% or 99.9%.

## What VaR backtesting is, and why it matters

This project counts how many times actual historical losses exceeded each method's VaR
estimate ("exceedances") and compares that count against the number expected purely from the
stated confidence level (`(1 - confidence) x number of days`). This is a simplified version of
the standard **Kupiec Proportion-of-Failures test** used in real risk management to validate
whether a VaR model's stated confidence level actually holds up against realized outcomes — a
risk model that isn't backtested against real exceedance rates is just an unverified
assumption, no matter how sophisticated its underlying math looks.
