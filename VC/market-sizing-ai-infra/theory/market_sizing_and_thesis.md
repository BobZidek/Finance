# Market Sizing (TAM/SAM/SOM) & Investment Thesis — Theory

## Why market sizing matters more at the venture stage than any other

A venture investment is a bet that a company can become large enough to return the fund (see
[`VC/portfolio-power-law-model`](../portfolio-power-law-model)) — which makes **market size
the single hardest constraint** on any early-stage thesis. A brilliant team and product can't
overcome a market that's fundamentally too small; conversely, a large enough market can support
multiple winners even with mediocre execution from any one of them. Market sizing is where a
VC memo starts, not an afterthought.

## TAM, SAM, SOM — three different questions

```
TAM (Total Addressable Market)      = the full market if this category captured 100% of spend
SAM (Serviceable Addressable Market) = the portion actually reachable by a given company's
                                        product, geography, and customer segment focus
SOM (Serviceable Obtainable Market)  = the realistic share a specific company could capture
                                        within a defined time horizon, given competition
```

TAM answers "is this category big enough to matter at all." SAM narrows to "how much of that
can *this kind* of company actually sell into." SOM narrows further to "how much can *this
specific* company realistically win," which is the number that actually determines whether an
individual investment can return a fund.

## Why top-down and bottom-up estimates should NOT match

This project deliberately builds **two independent TAM estimates**:

- **Top-down**: start from a large, well-known number (global enterprise software spend,
  ~$800bn) and apply a category-attribution percentage (~4%) — fast to build, but the
  attribution percentage is often a guess dressed up as precision.
- **Bottom-up**: start from a unit-level estimate (target enterprise count × average spend per
  enterprise) and multiply up — more defensible in its logic, but highly sensitive to the
  target count and spend-per-account assumptions, both hard to pin down for an emerging category.

In this project's run, the two methods diverge substantially in the base year (**$32.0bn
top-down vs. $7.5bn bottom-up** — more than 4x apart) and **converge somewhat but remain
meaningfully apart even 5 years out** ($109.95bn vs. $27.85bn). **This divergence is itself the
most useful output of the exercise** — a wide top-down/bottom-up gap signals genuine
uncertainty about market size that a single confident-sounding TAM slide would hide. This
project reports a **midpoint** as a working estimate while explicitly showing the range, rather
than picking whichever number sounds more impressive.

## Reading this project's SOM

At a **$24.1bn SAM by 2031**, a **1% obtainable share assumption** yields a **$241mm SOM** —
calibrated deliberately to represent a genuinely excellent, top-decile outcome for a single
infrastructure startup (roughly consistent with what a category-leading infrastructure company
might achieve in ARR within a 5-year horizon), not an average or typical result. Setting SOM%
too high (early drafts of this model used 4%, implying ~$965mm SOM) produces a number that
reads as unrealistic for a single company regardless of how good the underlying market is —
a common mistake in optimistic market-sizing slides worth flagging explicitly.

## The competitive landscape as a check on the thesis

`data/competitive_landscape.csv` and `output/competitive_landscape.csv` map five distinct
categories of competition: hyperscaler-native offerings, open-source projects, specialized
startups, retrofitted incumbent database vendors, and application-framework layers that sit
above the database and could commoditize it. **Two categories are flagged "High" threat**
(hyperscaler-native offerings and specialized startups) — meaning a credible investment thesis
in this space needs a specific, defensible answer to *both*: why won't a hyperscaler's
native/bundled offering be "good enough" for most customers, and what allows a given startup to
out-execute other well-funded specialized competitors chasing the same category. A thesis that
only addresses one of those two threats is incomplete.

## What a complete investment thesis adds beyond the numbers

This project provides the quantitative market-sizing backbone. A full investment memo (see
[`VC/investment-memo-startup`](../investment-memo-startup)) would combine this market analysis
with company-specific diligence: why this particular team, why this specific product wedge,
what the go-to-market motion looks like, and what evidence (early customer traction, retention,
expansion) suggests this company specifically can capture a meaningful share of the SOM modeled
here — market size alone never justifies an investment on its own.
