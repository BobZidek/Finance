# Football Field Valuation — Theory

## What it is

A "football field" chart is the standard way an investment bank presents a valuation
**conclusion** rather than a single methodology's output. Every valuation technique rests
on different assumptions and answers a slightly different question, so no single method is
treated as "the" answer — instead, 3-5 methodologies are run in parallel and their implied
ranges are stacked as horizontal bars on one chart (which, with several stacked ranges of
similar width, visually resembles yard markers on a football field — hence the name).

This project combines three methodologies to value a hypothetical private athletic apparel
company:

## Method 1 — Trading Comps (recap)

See [`IB/comps-analysis-fast-food/theory/comparable_company_analysis.md`](../comps-analysis-fast-food/theory/comparable_company_analysis.md)
for the full mechanics. In short: EV/EBITDA multiples from public peers, applied to the
target's own EBITDA, using the 25th-75th percentile as the range.

**What it captures:** current public market sentiment for similar, *minority-stake* businesses.
**What it misses:** a control premium — public share prices reflect the price of a single
share, not what a buyer would pay to acquire 100% of the company.

## Method 2 — Precedent Transactions

Precedent transactions look at **what acquirers have actually paid** for comparable companies
in historical M&A deals, rather than where peers currently trade. Multiples are calculated the
same way (EV/Revenue, EV/EBITDA) but from the **transaction** price, which is why they run
higher than trading comps: they embed a **control premium** — the extra amount buyers pay to
gain 100% ownership and control (this project's illustrative deals show ~25-40% control
premiums, in line with typical strategic/sponsor M&A).

**What it captures:** real-world pricing for a change-of-control transaction — the most
directly relevant benchmark if the target is actually being sold.
**What it misses:** deal-specific context (why did the premium vary — synergies? competitive
auction? distressed seller?) and market conditions at the time of each historical deal may not
match today's environment.

## Method 3 — DCF (recap)

See [`IB/dcf-model-semiconductors/theory/dcf_valuation.md`](../dcf-model-semiconductors/theory/dcf_valuation.md)
for full mechanics. This project's DCF ramps the target's EBITDA margin toward a terminal
margin assumption over the 5-year forecast, then applies a Gordon Growth terminal value. The
DCF's range here is generated from a WACC ± 0.75% band (a simplified version of the full
WACC × terminal-growth grid from the semiconductors DCF project).

**What it captures:** intrinsic value independent of current market sentiment.
**What it misses:** it's only as good as the forecast assumptions — garbage in, garbage out.

## Why the ranges differ (and what that tells you)

In this project's output, **precedent transactions produce the tightest, highest range**
(control premium embedded, less dispersion across only 6 illustrative deals), **trading comps
produce the widest range** (7 public peers with very different growth/margin profiles, no
control premium), and the **DCF sits toward the lower-middle** of the comps range. A banker
reading this would flag: the trading comps range is wide enough to be a weak anchor on its
own (driven by including both a high-growth peer like On Holding and a distressed peer like
Under Armour in the same set) — the precedent transactions and DCF bracket a tighter, more
credible range, which is where a "fair value" recommendation would likely land.

## Building the final recommendation

The overall recommended range is typically **not** simply "min of all methods to max of all
methods" — a banker would weight methodologies by relevance (e.g., precedent transactions
weighted heavily if the target is actually for sale; DCF weighted heavily if peers are a poor
match) and often narrow the peer set or precedent deal list further before finalizing. This
project reports the full overall range in `output/valuation_summary.txt` as a starting point
for that judgment call, rather than making the call automatically.
