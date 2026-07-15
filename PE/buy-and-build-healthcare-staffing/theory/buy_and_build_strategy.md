# Buy-and-Build Strategy — Theory

## What it is

A **buy-and-build** (or "roll-up") strategy acquires a **platform company** in a fragmented
industry, then uses it as a base to acquire smaller **bolt-on** (or "tuck-in") companies over
the hold period — consolidating a fragmented market into one larger, more valuable combined
entity. Healthcare staffing is a classic buy-and-build sector: highly fragmented (thousands
of small regional agencies), with real scale benefits (shared back-office, cross-selling
across specialties, national payer/hospital-system relationships smaller agencies can't access
alone).

## The core thesis: multiple arbitrage

The central economic engine of a buy-and-build is **multiple arbitrage**: small, single-owner
businesses typically sell for meaningfully **lower multiples** than a larger, more
professionalized platform — smaller companies carry more perceived risk (key-person
dependency, less diversified customer base, less audited financial history), and the buyer
pool for a $50mm-EBITDA business is much smaller than for a $500mm one. A sponsor exploiting
this pays the bolt-ons' lower multiples, but the *combined* entity — bigger, more diversified,
professionally run — commands the platform's higher multiple at exit.

```
Multiple Arbitrage = Exit Multiple − Weighted-Average Entry Multiple (across all acquisitions)
```

In this project's run: a **7.18x weighted-average entry multiple** (blending the platform's
8.0x with three bolt-ons bought at 6.0-6.5x) against a **9.5x exit multiple** — a **+2.32x
arbitrage spread**, applied to the entire combined EBITDA base at exit. That spread alone is
worth roughly $2.32 × $71mm ≈ $165mm of the deal's total value creation, independent of any
operational improvement.

## Integration synergies — the second value lever

Beyond multiple arbitrage, each bolt-on is assumed to generate **run-rate cost synergies**
(15% of its acquired EBITDA here) once integrated — shared back-office, procurement scale,
overhead elimination. This project models synergies ramping over 2 years post-acquisition
(0% in the acquisition year itself, 50% in year 1, 100% from year 2 onward) — mirroring the
same realistic ramp convention used in
[`IB/merger-model-airlines`](../../IB/merger-model-airlines), since integration takes real
time regardless of deal size.

## Why the debt schedule gets more complex

Unlike a single-deal LBO, buy-and-build financing involves **multiple debt draws at different
times** — new debt is raised at each bolt-on acquisition (2.5x turns on the bolt-on's own
EBITDA here, typically lower leverage than the platform's own entry leverage, since lenders
size bolt-on debt off the smaller add-on's standalone cash flow). This project tracks a single
**combined debt balance** that grows with each new draw and is swept down using the *combined*
entity's growing free cash flow capacity — meaning EBITDA growth (organic + synergies) directly
increases how fast the whole capital structure delevers, not just the original platform debt.

## Why MOIC/IRR need special handling here

Because sponsor equity is invested at **four different points in time** (platform close, plus
each bolt-on close), a simple "exit value ÷ entry value" MOIC would be misleading without also
accounting for *when* each dollar went in — a dollar invested at Year 3 (for Bolt-on 3) has
much less time to compound than a dollar invested at Year 0 (for the platform). This project
computes **total nominal equity invested** (simple sum across all four contributions, the
standard "money multiple" MOIC convention) alongside a **true IRR** that correctly weights
each contribution by its actual timing — reusing the same bisection-search IRR solver built
for [`PE/fund-model-waterfall`](../fund-model-waterfall), since the underlying problem (an
irregular series of cash outflows followed by one inflow) is identical.
