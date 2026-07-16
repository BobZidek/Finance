# Duration, Convexity & Key Rate Duration — Theory

## Duration: the first-order price sensitivity

**Modified Duration** approximates a bond's % price change for a small change in yield:

```
% Price Change ~= -Modified Duration x Yield Change
```

Mechanically, **Macaulay Duration** is the present-value-weighted average time until a bond's
cash flows are received (in years) — a bond with more cash flow received sooner (a short
maturity, or a high coupon that returns cash early) has a lower Macaulay duration than a
long-maturity, low-coupon bond, even at the same yield. **Modified Duration** rescales
Macaulay duration by `1/(1 + yield/periods per year)` to give the actual first-derivative price
sensitivity used in the formula above.

## Convexity: the second-order correction — and why it matters more than it looks

Duration is a **linear (first-order) approximation** to what is actually a **curved**
relationship between bond price and yield. For small yield moves, the linear approximation is
fine; for larger moves, it breaks down — and it breaks down in a **specific, predictable
direction**: because the true price-yield relationship is convex (curves upward), a bond's
price always rises by *more* than duration predicts when yields fall, and falls by *less* than
duration predicts when yields rise. **Convexity is always a benefit to the bondholder**, which
is exactly why the duration-only approximation in this project's price shock test is
systematically **too pessimistic on the downside and too optimistic on the upside** relative to
the actual re-priced bond.

```
% Price Change ~= -Modified Duration x Yield Change + 0.5 x Convexity x (Yield Change)^2
```

## This project's own results prove the point

For the longest-duration bond (Bond D, Modified Duration 13.23), at a **-300bp shock**:
- **Actual re-priced change: +52.26%**
- **Duration-only estimate: +39.69%** — an error of **-12.57 percentage points**, badly
  understating the true price gain.
- **Duration + Convexity estimate: +49.97%** — an error of only **-2.29 percentage points**,
  a roughly **5.5x reduction in approximation error** from adding the second-order term.

This is not a marginal refinement — for a large parallel yield move on a long-duration bond,
ignoring convexity produces a materially wrong risk estimate, which is exactly why real fixed
income risk systems always report both duration *and* convexity, never duration alone.

## Key Rate Duration: where along the curve is the risk, exactly?

A single duration number answers "how sensitive is this bond to yields moving?" but not
**which** yields — a portfolio can have the same overall duration while being concentrated in
short-end risk, long-end risk, or belly-of-the-curve risk, each with very different real-world
implications (a steepening curve, a Fed-driven front-end move, and a long-end inflation
repricing are economically different events). **Key Rate Duration (KRD)** answers this by
bumping **one point on the yield curve at a time** (1bp here) while holding all others fixed,
and measuring the resulting price change — repeated for every key maturity on the curve.

```
KRD_(key rate) = -(Price after bumping only that key rate - Base Price) / (Base Price x Bump Size)
```

This project's bonds sit **between** the curve's key maturities (3-year, 7-year, 12-year, and
20-year bonds against a curve defined at 2/5/10/30 years), so their yields are **linearly
interpolated** — and each bond's KRD is correctly **split across the two bracketing key
rates**, proportional to interpolation weight. Bond D (20 years, exactly halfway between the
10-year and 30-year key points) shows an almost perfectly even split: **KRD_10yr = 6.61 and
KRD_30yr = 6.61** — exactly what interpolation at the midpoint implies.

## A built-in correctness check: KRDs sum to modified duration

For every bond, **the sum of its Key Rate Durations across all four key maturities matches its
overall Modified Duration almost exactly** (e.g. Bond A: KRD sum 2.798 vs. Modified Duration
2.799) — this isn't a coincidence, it's a mathematical identity (shifting every key rate by the
same amount is equivalent to a parallel yield shift, which is what duration measures), and this
project verifies it explicitly as a correctness check on the KRD calculation, the same spirit
as the put-call parity check in
[`quant/options-pricing-black-scholes`](../options-pricing-black-scholes).
