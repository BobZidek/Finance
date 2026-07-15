# Buyout Capital Structure & Return Waterfall — Theory

## Why buyout equity isn't just "one class of stock"

In a leveraged buyout, the sponsor's equity check is rarely a single simple instrument. A
typical structure splits sponsor capital into **preferred equity** (senior to common, with a
contractual return) and a smaller slice of **common equity**, while **management** typically
"rolls over" some of their sale proceeds into common equity (aligning their incentives with
the sponsor) and receives an **option pool** as a forward-looking incentive grant. This
project models exactly that structure and how exit proceeds actually flow to each holder —
distinct from a VC-style priced-round cap table (see `VC/` for that) and from a *fund-level*
LP/GP carry waterfall across many deals (see [`PE/fund-model-waterfall`](../fund-model-waterfall)
for that different but related concept).

## The building blocks

- **Sponsor Preferred Equity**: the bulk of the sponsor's check (90% here). It carries a
  cumulative, compounding **preferred return** (8% here) — a contractual return that accrues
  whether or not the deal actually appreciates, and is senior to all common equity at exit.
- **Sponsor Common Equity**: a smaller slice (10% here) that participates directly in the
  upside alongside management, without the seniority the preferred carries.
- **Management Rollover**: management's own money (often proceeds they'd otherwise have
  received in the sale) reinvested into common equity — this is what "skin in the game"
  means literally, and sponsors typically require it as a condition of the deal.
- **Management Option Pool**: equity granted (not purchased) to incentivize management going
  forward, sized as a % of fully diluted common (10% here). Because it has **zero cost
  basis**, every dollar it receives at exit is pure profit — MOIC isn't a meaningful metric
  for it (division by zero invested capital), which is why the model reports it separately.

## Participating vs. non-participating preferred

This model uses **participating preferred**: the preferred class first gets its money back
plus its accrued preferred return (like *any* preferred), and **then also participates
pro-rata in the remaining upside alongside common**, as if it had converted. This is more
favorable to the preferred holder than **non-participating preferred**, which forces a choice
at exit between taking the preferred return *or* converting to common and taking a pro-rata
share — whichever is larger, but not both. Participating preferred is common in sponsor-led
buyouts precisely because it lets the sponsor capture senior, protected downside *and*
full exposure to the upside simultaneously.

## The waterfall, in order

```
Tier 1: Return of Preferred Capital        -> Sponsor Preferred only, up to its invested amount
Tier 2: Accrued Preferred Return           -> Sponsor Preferred only, cumulative compounding
Tier 3: Pro-rata Common Participation      -> ALL classes, including Preferred (as-converted)
```

Tier 2's accrued return compounds over the whole hold period:

```
Accrued Preferred Return = Invested Capital x ((1 + Preferred Rate)^Hold Years − 1)
```

Only **after** Tiers 1 and 2 are fully satisfied does any proceeds reach Tier 3, where every
class (preferred as-converted, sponsor common, management rollover, and the option pool)
shares pro-rata based on its unit count.

## Why the results look the way they do

In this project's run, **Sponsor Preferred earns 2.66x MOIC while Sponsor Common and
Management Rollover earn only 1.19x** on the same deal. That gap is the direct, mechanical
consequence of participating preferred's structure: the preferred class captures its senior,
protected return *first*, and *still* shares fully in the Tier 3 upside because it's
participating — common equity holders only get the Tier 3 slice. This is exactly why
management (holding only common/rollover, no preferred) cares intensely about deal structure
negotiations, not just the headline purchase price — the *split* of exit proceeds among
equity classes can matter as much to an individual holder's realized return as the deal's
overall performance.
