# The Kelly Criterion — Theory

## The question Kelly answers

Given a favorable, repeatable bet (or investment), **what fraction of your capital should you
risk each time** to maximize long-run wealth growth? Betting too little leaves genuine edge on
the table; betting too much — even on a favorable bet — can destroy long-run growth through the
mathematics of compounding, a genuinely counterintuitive result this project demonstrates
directly rather than just asserting.

## The formula, for a simple binary bet

```
f* = p - q/b
```

where `p` = win probability, `q = 1-p` = loss probability, and `b` = payoff ratio (how many
units you win per unit risked). This project's bet — 55% win probability, 1:1 payoff — gives
`f* = 0.55 - 0.45/1.0 = 10.0%`: **the Kelly-optimal strategy risks exactly 10% of current
wealth on each bet**, re-sizing after every outcome (betting a fraction of a growing or
shrinking bankroll, not a fixed dollar amount).

## Why Kelly maximizes the GEOMETRIC (not arithmetic) growth rate

```
Growth Rate(f) = p x ln(1 + bf) + q x ln(1 - f)
```

Kelly doesn't maximize *expected wealth* directly — it maximizes the **expected logarithm** of
wealth, which is mathematically equivalent to maximizing the long-run **geometric** (compound)
growth rate. This distinction matters enormously: **arithmetic** expected value per bet is
positive for *any* positive fraction as long as the bet itself has positive edge — but
**geometric** growth (what actually determines how your wealth compounds over many bets) is
maximized at exactly the Kelly fraction and can turn *negative* well before you'd expect,
purely from the effect of volatility drag on compounding.

## This project's results prove the point directly

| Strategy | Bet Fraction | Analytical Growth Rate | Median Terminal Wealth | Risk of Ruin |
|---|---|---|---|---|
| Half Kelly | 5.0% | +0.00375 | 7.22x | 0.0% |
| **Full Kelly** | **10.0%** | **+0.00501 (highest)** | **12.23x (highest)** | 0.6% |
| 2x Kelly (overbet) | 20.0% | **-0.00014 (negative!)** | **0.93x (below starting wealth!)** | 25.6% |
| Reckless (4x Kelly) | 40.0% | -0.04481 | ~0 | 98.2% |

**Full Kelly produces both the highest analytical growth rate and the highest median terminal
wealth across 2,000 simulated 500-bet paths** — exactly the theoretical prediction, verified
empirically via Monte Carlo rather than just asserted. **2x Kelly (still a seemingly modest
"overbet" — only double the optimal fraction) produces a *negative* growth rate**, meaning the
*typical* (median) outcome after 500 bets is to have **less** wealth than you started with —
despite every single bet in the sequence having a genuinely positive 55%/1:1 edge. This is the
single most important, and most commonly misunderstood, lesson about position sizing: **edge
alone doesn't guarantee long-run success — bet sizing relative to that edge determines whether
compounding works for you or against you.**

## Why "half Kelly" is common practice despite full Kelly maximizing growth

Full Kelly maximizes the *median/typical* outcome, but it does so with **meaningfully more
volatility and drawdown risk** along the way than a fraction of Kelly — real Kelly betting
produces genuinely uncomfortable, large swings even when it's mathematically "optimal." Half
Kelly gives up some growth rate (0.00375 vs. 0.00501, roughly 75% of full Kelly's growth rate)
in exchange for a **materially smoother ride** (0% risk of ruin at the 5%-of-starting-wealth
threshold, vs. 0.6% at full Kelly) — this trade-off, not a math error, is exactly why many real
practitioners (professional gamblers, some systematic trading desks) deliberately run at "half
Kelly" or another fraction below the theoretical optimum: **maximizing growth and minimizing the
psychological/practical cost of severe drawdowns are different objectives**, and full Kelly
only optimizes the first one.

## Risk of ruin — the tail risk Kelly alone doesn't fully address

Even Full Kelly carries a nonzero (0.6% here) probability of falling to a small fraction of
starting wealth across 500 bets — a reminder that "optimal" doesn't mean "safe." The catastrophic
degradation at 2x and 4x Kelly (25.6% and 98.2% risk of ruin, respectively) shows how quickly
that tail risk compounds once bet sizing meaningfully exceeds the theoretically justified
fraction — a genuinely important practical lesson for any form of leveraged or aggressively
sized position-taking, in gambling or in markets.
