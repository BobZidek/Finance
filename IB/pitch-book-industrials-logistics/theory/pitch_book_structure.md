# Full Pitch Book — Structure & Theory

## What a pitch book is

A pitch book is the deliverable an investment bank brings to a company (or its board) to win
an advisory mandate — typically for a sale process, capital raise, or strategic review. It
combines **market/industry context** with a **full valuation workup** and a **process
recommendation**. This project builds the analytical core (the four-methodology valuation)
that underpins a real pitch book; the sections below explain how it fits into the fuller
document a real deck would contain.

## Standard pitch book sections (and what this project covers)

1. **Executive summary** — the headline recommendation, one page. *(See "Recommendation" below.)*
2. **Industry overview** — sector dynamics, growth drivers, headwinds, competitive landscape.
   *(See "Industry context" below — narrative, not modeled.)*
3. **Company overview** — the target's business description, financial history, positioning.
   *(Represented here by `data/target_assumptions.csv` — a real deck would include several
   pages of qualitative + historical financial detail.)*
4. **Valuation — football field** — this project's core deliverable. Four methodologies:
   - **Trading Comps** — public peer multiples (see [`IB/comps-analysis-fast-food`](../comps-analysis-fast-food)).
   - **Precedent Transactions** — historical M&A multiples with control premiums (see
     [`IB/football-field-athletic-apparel`](../football-field-athletic-apparel)).
   - **DCF** — intrinsic value from projected cash flows (see [`IB/dcf-model-semiconductors`](../dcf-model-semiconductors)).
   - **LBO Ability-to-Pay** — new in this project; see below.
5. **Precedent transaction detail / process considerations** — buyer universe, likely process
   structure (auction vs. negotiated), timeline. *(Not modeled — qualitative judgment.)*
6. **Recommendation** — a specific proposed valuation range and process approach.
   *(See `output/recommendation.txt`.)*

## The fourth methodology: LBO Ability-to-Pay

Trading comps, precedent transactions, and a DCF all answer "what is this worth?" from
different angles. **Ability-to-pay** answers a different, very practical question: *"what is
the maximum price a **financial sponsor** (private equity buyer) could pay and still clear
their required return?"* It's standard in any pitch book where financial sponsors are a
plausible part of the buyer universe (true for most mid-market industrials/logistics deals).

Mechanically, it inverts the LBO returns model from
[`IB/lbo-model-healthcare-services`](../lbo-model-healthcare-services): instead of fixing an
entry multiple and solving for IRR, this project **fixes a target IRR (22%, with a ±2%
band for conservative/aggressive sponsors) and solves for the entry multiple** that produces
exactly that IRR, assuming a flat exit multiple (no multiple expansion) and standard
leverage/financing terms. That entry multiple, applied to EBITDA, becomes the implied EV for
the fourth football field bar.

## Why the LBO bar sits lowest here

A **financial sponsor** underwrites purely on the target's own standalone cash flow and
leverage capacity — no synergies, no strategic rationale, just "can debt service + equity
return work at this price?" A **strategic acquirer** (implicit in the precedent transactions
and, to some extent, trading comps ranges) can justify paying more because it can capture
cost and revenue synergies the target can't generate on its own. That's exactly what this
project's output shows: **LBO ability-to-pay ($854mm-$1,018mm) sits below every other
method** — a realistic and important pattern to recognize, not a modeling error. If a real
target's actual asking price sits meaningfully above the ability-to-pay ceiling, financial
sponsors will likely be priced out of the process, narrowing the buyer universe to strategics.

## Industry context (illustrative — general commentary, not company-specific)

The logistics/industrials transportation sector is shaped by a few well-known structural
dynamics worth noting in any real pitch book covering the space: (1) freight demand is
closely tied to broader economic/industrial production cycles, making the sector meaningfully
cyclical; (2) e-commerce growth has structurally increased parcel and last-mile volumes over
the past decade; (3) fuel price volatility and a persistent driver labor shortage pressure
carrier cost structures; (4) the sector has seen ongoing consolidation, as scale improves
network density and technology/data investment (load-matching, route optimization) increasingly
separates winners from laggards. These are general, well-known sector dynamics — not specific
claims about any named company — included here to illustrate the kind of narrative context a
real pitch book's industry section would develop in much greater depth.

## Building the recommendation

`output/recommendation.txt` proposes a range at the overlap of DCF, LBO ability-to-pay, and
precedent transactions — deliberately treating the (widest, least discriminating) trading
comps range as a sanity check rather than the primary anchor, since this project's peer set
mixes asset-light freight brokerages with asset-heavy carriers that structurally trade at very
different multiples. This mirrors how a banker synthesizes four ranges into one recommended
number: not a mechanical average, but a judgment call about which methodology is most credible
given the target's specific profile and the likely buyer universe.
