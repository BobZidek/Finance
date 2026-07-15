# Deal Screening Scorecard — Theory

## Where this fits in the PE deal process

Before any real diligence, valuation work, or management meetings, a PE firm typically
screens a large universe of potential targets (sourced from bankers, proprietary outreach,
or databases) down to a shortlist worth pursuing. With dozens or hundreds of candidates,
this first pass has to be **quantitative and fast** — a scorecard, not a full model, for
every name. This project builds that first-pass tool.

## The problem: combining metrics on different scales

A target universe naturally mixes metrics with completely different units and scales:
revenue growth (a %, typically single digits), EBITDA margin (a %, typically 10-30%), Net
Debt/EBITDA (a multiple, typically 0-4x), FCF conversion (a %), customer concentration (a %,
where *lower* is better). You can't just add these raw numbers together — a 3.5x leverage
figure and a 12% margin figure aren't comparable, and adding them would let whichever metric
happens to have the largest raw numbers dominate the score.

## The fix: z-scores (standardization)

```
z = (value − universe mean) / universe standard deviation
```

Converting every metric to a z-score expresses each company's value as **"how many standard
deviations above or below the peer universe average"** — a unit-free, directly comparable
scale. A company with EBITDA margin z = +1.2 and Net Debt/EBITDA z = −0.5 can now be sensibly
combined into a single number, because both are expressed in the same "standard deviations
from the group" units.

## Handling "lower is better" metrics

Not every metric wants a high raw value — lower leverage (Net Debt/EBITDA) and lower customer
concentration are *better* for a PE screen (more debt capacity headroom; less revenue risk
from losing a single customer). This project **flips the sign of the z-score** for those two
metrics (`scoring_weights.csv`'s `HigherIsBetter=False` column) so that "good" always
corresponds to a positive contribution to the composite score, regardless of which direction
the raw metric points.

## Weighting reflects investment priorities, not statistics

```
Composite Score = Σ (Metric Weight × Standardized, Sign-Adjusted Metric)
```

The weights (Growth 25%, Margin 20%, Leverage 20%, FCF Conversion 20%, Customer Concentration
15% here) are a **judgment call about what a PE screen should prioritize**, not derived
statistically — a growth-focused fund would weight revenue growth more heavily; a
credit-conscious fund evaluating a leveraged-heavy universe might weight Net Debt/EBITDA
more heavily. Changing the weights (in `data/scoring_weights.csv`) changes the ranking
without touching the code — the weighting choice itself is the analytical judgment a real
associate would defend to their investment committee.

## Reading the breakdown chart, not just the ranking

`output/score_breakdown.png` shows each target's composite score decomposed by factor — this
matters because two companies can land at similar overall ranks for very different reasons.
In this project's output, **Clearwater Pool Services** ranks #1 largely on strong growth, high
FCF conversion, and low customer concentration; **Coastal Marina Management** ranks a close #2
primarily on best-in-class margin and FCF conversion despite more moderate growth. Knowing
*why* a target scored well is exactly what a screening memo needs to say before recommending
it for deeper diligence — the composite number alone isn't the deliverable.

## What a scorecard is (and isn't)

This ranking is a **prioritization tool for where to spend diligence time next**, not a
valuation or investment decision. A high-scoring company might still fail diligence on
qualitative factors (management quality, competitive moat, deal-specific complications) that
no quantitative scorecard captures — which is exactly why it feeds *into* a process, rather
than replacing the process.
