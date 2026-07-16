# Sum-of-the-Parts (SOTP) Valuation — Theory

## Why a single multiple can misprice a diversified company

Standard trading comps ([`IB/comps-analysis-fast-food`](../comps-analysis-fast-food)) apply one
peer multiple to a company's consolidated EBITDA — which works well when a company operates in
a single business, but **breaks down for a diversified conglomerate** whose segments belong to
structurally different industries with different growth rates, margins, capital intensity, and
market-clearing multiples. Applying one blended multiple to the whole company implicitly forces
every segment to be valued as if it were the *average* business — systematically mispricing
both the highest-quality segment (undervalued, since its true multiple is higher than the
blend) and the lowest-quality segment (overvalued, for the opposite reason), and the two errors
don't fully offset in a way that gives the right total.

## The SOTP method

```
For each segment: Segment EV = Segment EBITDA x Segment's OWN Peer Multiple
Total Segment EV = Sum of all Segment EVs
Less: Capitalized Corporate Overhead = Unallocated Corporate EBITDA (a cost, so negative) x
      an appropriate multiple (often a low, cost-center multiple - it generates no revenue)
SOTP Enterprise Value = Total Segment EV − Capitalized Corporate Overhead
SOTP Equity Value = SOTP Enterprise Value − Net Debt
```

Each segment is valued using the trading multiple of **its own** pure-play peer group (here:
11.5x for Aerospace & Defense, which trades rich on programmatic revenue visibility and margin
quality; 9.0x for Building Products; 8.0x for Specialty Chemicals, generally the most cyclical
and capital-intensive of the three) — giving each business credit for its own market-clearing
value rather than forcing a single average multiple on all of them.

## Corporate overhead: a real, capitalized cost, not an afterthought

Unallocated corporate costs (executive compensation, public company costs, shared services not
charged back to segments) reduce consolidated EBITDA but don't belong to any one segment. This
project **capitalizes that cost as its own negative "segment"** at a modest multiple (7.0x here
— lower than any actual operating segment's multiple, since a pure cost center generates no
revenue growth to justify a premium) rather than ignoring it or arbitrarily allocating it —
$45mm of overhead capitalized at 7.0x is a real $315mm value drag that a rigorous SOTP analysis
must account for.

## The conglomerate discount — quantified, not just asserted

```
Conglomerate Discount = (SOTP EV − Current Trading EV) / SOTP EV
```

This project's result: **SOTP Enterprise Value of $4,370mm vs. current trading value of
$3,612.5mm (at the company's blended 8.5x multiple)** — implying a **17.3% conglomerate
discount**, and a **27.4% per-share upside** ($29.33 SOTP vs. $23.02 current) if the company
were valued at its parts' true worth. This is exactly the analytical basis activist investors
and management teams use to justify — or resist — a spin-off, split-off, or divestiture: **the
SOTP calculation quantifies the specific dollar amount of value a break-up could unlock**,
turning "conglomerates often trade at a discount" from a vague market observation into a
company-specific, defensible number.

## Why a real SOTP analysis is more contested than this simplified version

Real conglomerate discount debates are rarely settled purely by the arithmetic above — bulls
on the current structure argue the conglomerate offers real diversification and cross-segment
synergies (shared R&D, procurement scale, internal capital allocation flexibility) that would
be **lost** upon separation, partially or fully offsetting the multiple-arbitrage gain this
model implies. A complete real-world analysis would net the SOTP upside against the estimated
value of dis-synergies from separation — this project's `ENHANCEMENTS.md` outlines how to add
that.

## Reading the sensitivity table

`output/multiple_sensitivity.csv` sweeps all three segment multiples up and down together
(±1.5x in 0.5x steps) — showing that the SOTP conclusion is directionally robust across a wide
range of multiple assumptions, not dependent on hitting the exact base-case multiples exactly.
This is standard practice before presenting a SOTP thesis: confirming the upside conclusion
survives reasonable multiple compression, not just the specific point estimate used.
