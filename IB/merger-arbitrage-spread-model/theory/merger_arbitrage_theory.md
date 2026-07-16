# Merger Arbitrage — Theory

## What merger arbitrage actually is

Once an M&A deal is announced, a target's stock typically trades **below** the announced deal
price — the gap (the "spread") compensates investors for the risk the deal doesn't close
(antitrust blocks, financing falls through, shareholder vote fails, a material adverse change
is invoked) and for the **time value** of waiting for the deal to actually close. **Merger
arbitrage** is the strategy of buying the target at this discount and profiting from the spread
converging to zero as the deal closes — a strategy whose returns depend almost entirely on
**deal-specific completion risk**, not general market direction, which is why merger arb funds
are often marketed as "market neutral."

## Gross spread and annualized spread

```
Gross Spread = Deal Price − Current Price
Gross Spread % = Gross Spread / Current Price
Annualized Spread % = Gross Spread % x (365 / Days to Close)
```

In this project: a **$2.50 gross spread (5.05%)** on a deal expected to close in ~6 months
annualizes to **10.1%** — but this annualized figure is the return **only if the deal closes
with certainty**, which it never does. Quoting only the annualized spread without the
completion-probability context is a common way merger arb returns get overstated.

## Backing out the market's own probability estimate

If the target's current price reflects the market's collective view of the deal's odds, then:

```
Current Price = P(close) x Deal Price + (1 − P(close)) x Downside Price (if deal breaks)
```

Solving for `P(close)`:

```
P(close) = (Current Price − Downside Price) / (Deal Price − Downside Price)
```

This project's market-implied probability of close is **79.17%** — a genuinely useful,
extractable signal about what the market believes, distinct from what any individual investor
believes. **This market-implied probability is, by construction, also the exact breakeven
probability** — at that probability, expected return is precisely zero, since that's the
definition of the price the market has already set. Understanding this tautology matters: the
market-implied probability isn't a prediction *of* what will happen, it's a description of what
the *current price already assumes will happen*.

## Why an investor's own view matters — and how to act on it

A merger arbitrageur doesn't trade the market-implied probability — they trade their **own**
independently-formed view against it. This project's analyst believes the deal is **more**
likely to close (90%, reflecting confidence in the strategic rationale, a clean antitrust
profile, and committed financing) than the market's implied 79.17%:

```
Expected Price = P(close, analyst view) x Deal Price + (1 − P) x Downside Price
Expected Return = (Expected Price − Current Price) / Current Price
```

At the analyst's 90% view, expected return to close is **+2.63% (5.25% annualized)** — a
genuine, positive edge relative to the market's implied assumption, even though it's far
smaller than the naive "certain-close" annualized spread of 10.1%. **The entire investment
thesis boils down to whether the analyst's probability view is better-informed than the
market's** — merger arbitrage is fundamentally a bet on your own diligence into deal-specific
risk (regulatory review status, financing commitment letters, shareholder vote dynamics)
outperforming the market's aggregate assessment.

## The asymmetric risk profile — the defining feature of merger arb

```
Upside if deal closes:  +$2.50/share (+5.05%)
Downside if deal breaks: -$9.50/share (-19.19%)
```

This is the structural signature of merger arbitrage: **a small, high-probability gain against
a much larger, lower-probability loss** — almost the mirror image of buying an out-of-the-money
option. A merger arb portfolio's returns look like a steady stream of small positive spreads
punctuated by occasional sharp losses when individual deals break — which is exactly why
**diversification across many uncorrelated deals**, and rigorous deal-specific risk assessment
(not just chasing the widest spread), is central to how real merger arb funds are managed —
a single deal's binary risk is far too large to bet the portfolio on.
