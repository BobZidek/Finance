# The VC Method — Theory

## Why early-stage valuation works backward

Early-stage startups rarely have meaningful revenue or cash flow to build a DCF from, and
there's usually no public peer set with a comparable business model and stage — the two
inputs comps and DCF valuation both depend on. The **VC Method** sidesteps this by working
**backward from the outcome the investor needs**: assume a plausible future exit value, decide
what return multiple justifies the risk of an early-stage bet, and solve for what ownership
(and therefore what valuation) makes that return achievable.

## The core formula

```
Target Ownership at Exit = (Investment x Required ROI) / Exit Value
Post-Money Valuation      = Investment / Required Ownership
Pre-Money Valuation        = Post-Money Valuation − Investment
```

`Required ROI` (here, 15x) reflects the return a venture investor needs on a single deal to
compensate for **portfolio-level risk** — most early-stage investments fail entirely or return
less than invested capital, so the handful of winners in a fund's portfolio need to return
enough to cover those losses and still deliver the fund's overall target return (see
[`VC/portfolio-power-law-model`](../portfolio-power-law-model) for exactly how that
portfolio-level math works). A single-digit ROI target would be appropriate for a much later,
lower-risk stage; 10-30x is typical for seed/Series A-stage bets.

## The mistake most simplified versions make: ignoring future dilution

A startup raising a seed or Series A round will almost always raise **more rounds** before any
exit — each of which dilutes every existing shareholder, including this round's investor. If
today's investor needs to own 15% of the company **at exit** to hit their target return, they
need to own **more than 15% today**, because their stake will shrink with every subsequent
financing round between now and the exit.

```
Retention Ratio = Π (1 − Dilution % of each anticipated future round)
Required Ownership TODAY = Target Ownership at Exit / Retention Ratio
```

In this project, two anticipated future rounds (Series B at 20% dilution, Series C at 15%
dilution) combine to a **68.0% retention ratio** — meaning only 68% of today's ownership
"survives" to exit. That pushes required ownership today from 15.0% up to **22.1%** — and
because required ownership is the denominator in the post-money valuation formula, a *higher*
required ownership % means a *lower* achievable valuation for the same investment amount.

## Reading this project's result

**Ignoring future dilution overstates the achievable pre-money valuation by ~$10.67mm (60%)**
in this run — $28.33mm (naive) vs. $17.67mm (dilution-adjusted) for the same $5mm check, same
exit assumption, and same required return. This is not a rounding-error-sized correction — it's
the difference between a founder-favorable and a much more conservative valuation, and it's
exactly why any VC Method calculation that skips the dilution adjustment should be treated as
directionally wrong, not just imprecise.

## Why the sensitivity table matters more than any single number

Both core inputs — the eventual exit value and the required return multiple — are **genuinely
uncertain forecasts**, not facts. The sensitivity grid (Exit Value × Required ROI) makes that
uncertainty explicit: the same deal's defensible pre-money valuation ranges from **$1.8mm**
(30x ROI target, $300mm exit) to **$46.0mm** (10x ROI target, $750mm exit) across plausible
assumption combinations — a >25x spread. This is exactly why VC valuation negotiations are as
much about **which assumptions to use** as about the arithmetic itself; the formula is simple,
but the inputs are where the real judgment (and negotiation leverage) lives.
