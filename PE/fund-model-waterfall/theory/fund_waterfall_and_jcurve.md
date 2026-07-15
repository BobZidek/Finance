# Fund-Level Model: J-Curve & GP Carry Waterfall — Theory

## Why fund-level modeling is different from deal-level modeling

Every other project in this repo models a single deal. A **PE fund** is a portfolio of many
deals with staggered entry and exit timing, funded by Limited Partners (LPs) who commit
capital upfront but only actually wire cash when the fund "calls" it, and who only receive
cash back as individual portfolio companies exit — which can be years apart. Fund-level
economics (what an LP actually experiences) depend not just on how good the individual deals
are, but on **when** capital goes in and comes out, and on the fee and carry structure sitting
between gross deal performance and what the LP actually receives.

## The J-curve

```
Cumulative LP Net Cash Flow_t = Cumulative LP Net Cash Flow_(t-1) + (LP Distributions_t − Capital Calls_t)
```

Early in a fund's life, capital calls (deal investments + management fees) far outpace
distributions (no deals have exited yet) — cumulative LP cash flow goes **negative** and stays
there for years. As deals begin exiting (years 5+ in this model), distributions accelerate and
eventually overtake cumulative calls, turning the curve positive. Plotted over the fund's
life, this traces the characteristic **J shape** that gives the pattern its name — and it's
why a young fund's *interim* IRR (before any exits) is structurally negative or meaningless,
which is exactly why LPs evaluate young funds on pacing and portfolio quality, not on
early-vintage IRR.

## Management fees are LP capital, too

The management fee (2% of committed capital during the 5-year investment period, then 2% of
remaining unrealized cost afterward — a standard fee stepdown) is **called from LPs just like
investment capital**, and — critically — **counts toward the capital that must be returned
(with the preferred return accruing on it) before any carry is paid**. This project's waterfall
correctly folds management fees into `TotalCapitalCalls` in the running "unreturned capital"
balance, exactly as a real fund agreement would.

## The waterfall, tier by tier (European / whole-fund basis)

This model runs a **European waterfall** — carry is calculated on the fund as a whole, only
after LPs have gotten back 100% of *all* contributed capital (across every deal) plus the
preferred return. This is more LP-friendly than an **American (deal-by-deal) waterfall**,
where the GP can earn carry on an early winning deal even while later deals are still unrealized
or underperforming — see `ENHANCEMENTS.md` for building that comparison.

Each year, available distributions flow through four tiers **in order**, and a single year's
distribution can spill through multiple tiers if it's large enough:

```
Tier 1: Return of Capital     -> LP, until cumulative unreturned capital is fully repaid
Tier 2: Preferred Return      -> LP, until the 8% cumulative compounding hurdle is fully paid
Tier 3: GP Catch-up           -> GP, 100%, until GP has caught up to 20% of total profit distributed so far
Tier 4: Residual Split        -> 80% LP / 20% GP, on everything remaining
```

**Preferred return accrues every year on the outstanding unreturned capital balance** —
increasing the hurdle the fund must clear before any carry flows, exactly like the
participating preferred mechanics in [`PE/buyout-waterfall-cap-structure`](../buyout-waterfall-cap-structure),
just applied across the whole fund's cash flow history rather than a single deal.

## The GP catch-up formula

```
GP Catch-up Target (cumulative) = (Carry% / (1 − Carry%)) × Cumulative Preferred Return Paid to LP
```

This target is exactly the amount of GP catch-up that makes the GP's cumulative carry equal
**20% of total profit distributed so far** (LP's preferred return + GP's catch-up), which is
the entire point of a "100% catch-up" provision — it's a clawback-avoidance mechanism ensuring
the GP eventually reaches its full 20% economic share of profits, not just 20% of amounts
above the hurdle going forward.

## Reading this project's results

- **Gross Fund MOIC (deal-level, before fees/carry): 1.99x** — this is what the portfolio
  companies themselves actually returned.
- **LP Net TVPI: 1.60x** and **LP Net IRR: 10.8%** — what the LP actually receives, after
  ~$78.5mm of GP carry and years of management fees. The gap between 1.99x gross and 1.60x
  net (a "fee and carry drag" of ~0.39x) is exactly the cost of the fund structure — a real
  and material number LPs scrutinize closely when comparing funds and vintage years.
- **GP carry doesn't start flowing until Year 8** — the exact year cumulative distributions
  finally clear the return-of-capital and preferred-return hurdles built up over 7 years of
  capital calls. Before that, 100% of every distributed dollar goes to LPs.
