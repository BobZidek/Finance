# Growth Equity & Structured Minority Investing — Theory

## How growth equity differs from both buyouts and early-stage VC

Growth equity sits between the two other private capital strategies covered in this repo.
Unlike a **buyout** ([`PE/full-lbo-model-business-services`](../full-lbo-model-business-services)),
growth equity investments are typically **minority, non-control stakes with little or no
leverage** — the investor isn't buying the company, just backing its next stage of growth with
capital, and management retains control. Unlike early-stage **VC**
([`VC/term-sheet-analyzer`](../../VC/term-sheet-analyzer)), growth equity targets more mature,
already-revenue-generating companies, and its preferred structures are typically **less
aggressive on participation** (often non-participating, as here) but add a feature VC term
sheets rarely include: an explicit **redemption right**.

## The three components of this structure

### 1. Cumulative PIK dividend — protecting downside without straining company cash

```
Accreted Liquidation Preference = Investment x (1 + PIK Rate)^Years Held
```

A **PIK (payment-in-kind)** dividend accrues to the liquidation preference balance rather than
requiring a cash payment from the company — critical for a growing company that needs to
reinvest cash into the business rather than service investor distributions. The 8% rate here
compounds the investor's minimum protected value every year the investment is outstanding,
independent of whether the company's equity value actually grows.

### 2. Non-participating liquidation preference — a real floor, not a double-dip

Unlike the participating preferred modeled in
[`PE/buyout-waterfall-cap-structure`](../buyout-waterfall-cap-structure), this structure is
**non-participating**: at exit, the investor takes the **greater of** converting to common
(sharing pro-rata in the company's actual value) **or** the accreted liquidation preference —
never both. This project's three scenarios show exactly when each path wins:

- **Strong Growth ($600mm exit)**: as-converted value ($132mm) exceeds the accreted preference
  ($97.1mm at 5 years) — investor **converts to common**, sharing fully in the upside.
- **Modest Growth ($250mm exit)**: as-converted value ($55mm) falls **below** the accreted
  preference ($117.6mm) — investor **takes the liquidation preference instead**, protecting
  its downside even though the company technically grew from its starting valuation.

### 3. Redemption right — the feature that makes growth equity structurally distinct

```
Redemption Value = MAX(Accreted Liquidation Preference, Investment x (1 + Minimum IRR)^Years)
```

If the company hasn't achieved a **qualified liquidity event** (IPO, sale) within a set window
(6 years here), the investor gains the right to **force the company to redeem** (buy back) its
shares — at whichever is larger: the PIK-accreted cost, or a **minimum IRR floor**. This is a
genuinely different mechanic from anything else modeled in this repo: it's not contingent on an
exit happening at all — it's a **put option against the company itself**, existing specifically
to protect investors from a scenario where the company simply never generates a liquidity
event, stagnating indefinitely rather than growing or explicitly failing.

In this project's stagnant scenario, the **12% IRR floor ($157.9mm) exceeds the pure PIK
accretion ($95.3mm at 6 years)** — the IRR floor is the binding, more valuable protection,
guaranteeing the investor a minimum *return*, not just a minimum *nominal* payback.

## Why this structure exists: growth equity's fundamentally different risk profile

A growth equity investor is betting on a company that's already proven meaningful traction —
lower risk than a seed-stage VC bet, but still real risk that growth stalls before an exit
materializes. **The redemption right specifically insures against the "zombie company" outcome**
— a business that neither fails outright nor achieves a liquidity event, simply persisting
indefinitely without ever returning capital. Pure common equity (or even standard VC preferred
without redemption rights) offers no protection against this scenario; a growth equity
redemption right converts an indefinite wait into a defined-horizon claim with a guaranteed
minimum return, which is exactly the kind of downside engineering that distinguishes
structured minority investing as its own discipline within private capital.
