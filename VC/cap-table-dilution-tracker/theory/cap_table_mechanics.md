# Cap Table & Dilution Mechanics — Theory

## Why this is harder than it looks

A cap table is conceptually simple — track who owns what, and how new financing dilutes
existing holders. In practice, two mechanics make it genuinely tricky to get right: **SAFE
conversion** (when does a discount vs. a cap actually bind, and what shares does an
uncertain-instrument even convert into?) and the **option pool "shuffle"** (a top-up sized
as a % of the post-round cap table, but funded entirely by pre-money holders). Both are
modeled explicitly and correctly here — most simplified cap table tutorials skip both.

## SAFEs: convertible instruments, not equity (yet)

A SAFE (Simple Agreement for Future Equity) is **not a share of stock** — it's a right to
receive equity at a **future priced round**, at whichever conversion price is more favorable
to the investor between two mechanisms:

```
Cap Price      = Valuation Cap / Pre-round Fully Diluted Shares (excluding this round's new
                  pool and new money - the "capitalization" the cap is measured against)
Discount Price = New Round Price Per Share x (1 - Discount %)
Conversion Price = min(Cap Price, Discount Price)     <- lower price = more shares for the investor
```

**Why this is circular**: the discount price depends on the new round's price per share —
but the new round's price per share depends on the pre-money share count, which *includes*
the SAFEs that are converting *right now*. This project resolves that circularity with a
small **iterative solver** (`process_seed_and_series_a` in the code): guess SAFE shares → compute
round pricing → recompute SAFE shares from the resulting price → repeat until stable. This
converges in a handful of iterations because it's a contraction mapping, and it's exactly
how real cap table software (Carta, Pulley) resolves the same circularity.

In this project's run, **SAFE 1's cap ($8M) is the binding constraint** (cap price $0.727/share
beats its discount price of ~$0.865/share), while **SAFE 2 has no discount**, so its cap is
the only lever. Neither SAFE ends up "using" its discount in this scenario — worth checking in
any real cap table, since which mechanism binds isn't obvious without running the actual math.

## The option pool "shuffle" — the single most misunderstood mechanic in VC

When a new round includes an option pool top-up (common at Series A, since seed-stage pools
are usually too small to support post-Series-A hiring), the target is almost always expressed
as **a % of the POST-money cap table**. But the pool shares themselves are added to the
**pre-money** share count — meaning **the new investor pays nothing for the pool dilution**;
it's borne entirely by existing (pre-money) holders, overwhelmingly founders at this stage.

```
Target Pool % = New Pool Shares / Post-Money Fully Diluted Shares
```

Solving this algebraically (see `solve_pool_topup` in the code) for the pre-money fully
diluted share count `x`:

```
x = (S_old x Pre-Money) / (Pre-Money - Target_Pool% x Post-Money)
```

This project's Series A includes a top-up to a 15% post-money pool. Because the pool dilutes
pre-money holders (founders + converting SAFEs) but not the incoming Series A investor, **the
founders' effective dilution from Series A is larger than a naive "new investor gets X% of the
company" calculation would suggest** — this is a real, material effect worth flagging in any
negotiation, and exactly why sophisticated founders push back on oversized pool top-ups.

## Reading the dilution trajectory

Founder ownership falls from **90.9% at founding to 36.1% after Series C** across four
financing events — each round diluting existing holders by roughly the same proportion the new
money represents of the post-money valuation, compounded by the Series A pool top-up. This
trajectory (roughly halving founder ownership every 1-2 rounds in the early stages, then
slowing as later rounds are proportionally smaller relative to a much larger valuation) is
typical for a venture-backed company through Series C, and is exactly the shape a founder
should expect and plan for when negotiating early-stage terms.
