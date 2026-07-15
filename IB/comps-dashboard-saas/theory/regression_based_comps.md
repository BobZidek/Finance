# Regression-Based Comps — Theory

## The problem with a flat median multiple

The basic comps approach ([`IB/comps-analysis-fast-food`](../comps-analysis-fast-food)) applies
a single median (or percentile range) multiple to every company in the peer set, implicitly
assuming the target is "average" relative to its peers. But within any sector, peers differ
systematically on the two things that most drive valuation multiples: **growth** and
**profitability**. A flat median multiple either overvalues a below-average grower or
undervalues an above-average grower — precision is lost exactly where it matters most.

SaaS is the sector where this matters most, because growth rates vary enormously even
within "the SaaS peer set" (9% to 29% in this project's data) and the market prices that
dispersion explicitly.

## The fix: regress the multiple against the driver

```
EV / Revenue = β₀ + β₁ × Revenue Growth  (simple linear regression, OLS)
```

Fitting this line across the peer set produces a **predicted multiple as a function of
growth**, rather than one fixed number. Applying it to a target's own growth rate produces
a **growth-adjusted implied multiple** — in this project's run, a target growing at 20% gets
a predicted multiple of ~12.6x vs. the flat peer median of ~10.5x, a ~20% difference in
implied value purely from correcting for the fact that the target grows faster than the
median peer.

**R² (0.64 in this run)** tells you how much of the multiple dispersion growth actually
explains — a genuinely useful diagnostic. An R² near 1.0 would mean growth alone almost
fully explains market pricing (comps regression is highly reliable); an R² near 0 would mean
growth explains almost nothing (something else — profitability, market position, risk — is
driving pricing, and a single-factor regression isn't the right tool).

## Reading the residuals: over/under-valued flags

The **residual** for each peer (actual multiple − regression-predicted multiple) measures how
much of that peer's multiple *isn't* explained by growth alone. A large positive residual
(like CrowdStrike's +2.67 here) means the market is paying more than growth alone would
predict — plausibly for superior margins, category leadership, or a premium narrative. A
large negative residual (like Zscaler's −2.54) means the opposite. This project flags any
peer more than 0.5 standard deviations from the regression line as "Overvalued" or
"Undervalued" relative to peers *on a growth-adjusted basis* — not an absolute valuation
call, just a relative-to-the-regression-line one.

## Rule of 40 — a second lens

```
Rule of 40 = Revenue Growth % + FCF Margin %
```

A common SaaS heuristic: companies scoring ≥40 are considered to be in a healthy
growth/profitability balance — either growing fast (even at low margin) or profitable
(even at low growth) is fine, but scoring low on *both* is a red flag. It's included here as
a second, independent screen alongside the growth-vs-multiple regression, since a company
can screen as "undervalued" on the regression while still scoring poorly on Rule of 40 (worth
checking both before concluding a peer is a genuine bargain).

## Why a two-factor model would be better (and what's next)

This project intentionally uses a **single-factor** regression (growth only) for clarity and
because it's easy to visualize on one scatter plot. A more rigorous version would add
profitability (FCF margin, or the Rule of 40 score itself) as a second independent variable
in a multiple regression — see `ENHANCEMENTS.md`.
