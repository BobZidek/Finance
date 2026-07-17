# Management Equity Incentive Plans & Ratchets — Theory

## Why a flat pro-rata split doesn't align incentives well enough

[`PE/buyout-waterfall-cap-structure`](../buyout-waterfall-cap-structure) modeled a fixed
sponsor/management ownership split with participating preferred — management's % ownership
was set once at close and stayed constant regardless of how well the deal performed. A **ratchet**
goes further: management's *share of exit proceeds* itself **increases in tiers** as overall
deal performance improves — meaning management isn't just aligned with the sponsor's success in
direction, they're increasingly aligned with it in *magnitude*. A ratchet is specifically
designed to reward exceptional outcomes disproportionately, not just good ones.

## The mechanics: tiered participation by deal performance

```
Total Deal MOIC = Total Exit Equity Value / Total Initial Invested Equity (Sponsor + Management)

Tier 1 (MOIC < 2.0x):        Management gets 10% of total exit proceeds
Tier 2 (2.0x <= MOIC < 3.0x): Management gets 15%
Tier 3 (3.0x <= MOIC < 4.0x): Management gets 20%
Tier 4 (MOIC >= 4.0x):        Management gets 25%
```

At each exit scenario, management's proceeds are computed at the tier's specified percentage
of *total* exit value — not a fixed dollar formula, but a genuinely different share of the pie
depending on how large that pie turns out to be.

## Why management's MOIC explodes even faster than their ownership % suggests

Management's **initial investment is small relative to the sponsor's** ($5mm vs. $200mm in
this project) — a deliberate design choice, since most operating executives simply don't have
$200mm of personal capital to put at risk, but sponsors still want genuine "skin in the game."
This means even a **modest percentage** of total exit proceeds translates into an **enormous
MOIC** on management's small initial check. This project's results show exactly that dynamic:

| Exit Value | Management Share | Sponsor MOIC | Management MOIC |
|---|---|---|---|
| $300mm | 10.0% | 1.35x | **6.0x** |
| $820mm | 25.0% | 3.08x | **41.0x** |
| $1,200mm | 25.0% | 4.50x | **60.0x** |

At the highest exit scenario, **management's MOIC (60.0x) is more than 13x the sponsor's own
MOIC (4.50x)** on the same deal outcome — not because management somehow "beat" the sponsor,
but because the ratchet mechanism combined with management's tiny initial check structurally
amplifies their return far beyond the sponsor's, by design.

## Why sponsors deliberately design it this way

A rational sponsor giving away a disproportionate share of upside to management seems
counterintuitive until you consider the alternative: **the sponsor's own return is a direct
function of total deal value, and a well-incentivized management team drives that total value
higher than a merely-adequately-incentivized one would.** The ratchet only pays out
meaningfully in the tiers where the sponsor is *also* doing exceptionally well (3-4x+ MOIC) —
management earning 60x only happens in a scenario where the sponsor has already earned 4.5x.
The sponsor is effectively saying: "we'll give up a growing share of an outcome that's already
excellent for us, specifically to make that excellent outcome more likely." This is a genuinely
different logic than simple ownership dilution — it's a **deliberately engineered incentive
structure**, and precisely calibrating the tier boundaries and percentages (too generous and
the sponsor gives away too much value; too conservative and management isn't meaningfully
incentivized to chase the top tier) is real, substantive deal-structuring work in private
equity, not a mechanical afterthought.

## The connection to the participating preferred structure elsewhere in this repo

This ratchet mechanic can (and often does) sit **on top of** the participating preferred
structure from [`PE/buyout-waterfall-cap-structure`](../buyout-waterfall-cap-structure) — a
real deal might have sponsor preferred equity earning its return first, *then* a ratcheted
split of the remaining common proceeds between sponsor and management based on the tier
achieved. This project isolates the ratchet mechanic on its own for clarity; a fully combined
model is a natural next step (see `ENHANCEMENTS.md`).
