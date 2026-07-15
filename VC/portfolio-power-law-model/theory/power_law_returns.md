# The VC Power Law — Theory

## Why VC portfolio math is fundamentally different from other asset classes

In most investing contexts, returns cluster around a mean — a diversified stock portfolio's
holdings mostly move within a modest range of each other. **Venture capital returns don't work
that way.** Startup outcomes are famously bimodal-to-extreme: the large majority of early-stage
companies fail or return less than invested capital, while a small handful of outsized winners
generate returns so large they single-handedly determine whether the *entire fund* succeeds.
This is the **power law** — and it's the single most important thing to understand about how
VC portfolio construction and fund economics actually work, distinct from the more "normal
distribution" thinking that governs public-market portfolio theory.

## Quantifying concentration: this project's portfolio

Across 20 hypothetical investments (each a $1.5mm check, $30mm total deployed):

```
Total Proceeds: $223.2mm  ->  Fund Gross MOIC: 7.44x
```

But that headline 7.44x hides enormous concentration:

- **The single best investment (Company T, 65x) alone contributes 43.7% of total proceeds.**
- **The top 3 investments contribute 72.6%** of total proceeds.
- **The top 5 investments (25% of the portfolio) contribute 86.0%.**
- **40% of all investments returned below 1x** — meaning the fund's strong overall MOIC
  coexists with a large fraction of individually money-losing decisions.

If you removed just the single best investment from this portfolio, fund proceeds would fall
from $223.2mm to $125.7mm — a **44% drop in total fund value from one deal's outcome**. This
is the mathematical reality every VC fund lives with: a small number of decisions (which
companies to back, and — just as importantly — how much follow-on capital to commit to the
apparent winners) matter enormously more than the median decision.

## Why this changes how VCs think about portfolio construction

1. **Diversification works differently.** More portfolio companies increases the *chance* of
   catching an outlier winner, but doesn't reduce risk the way diversification does in public
   markets — a VC fund's success still hinges on catching at least one or two power-law
   outcomes, not on the average behaving predictably.
2. **"Spray and pray" vs. concentrated conviction is a real strategic choice.** Some funds
   place many small bets to maximize the chance of catching an outlier; others make fewer,
   larger, higher-conviction bets. Both are coherent strategies *given* the power law — but they
   imply very different check sizes, ownership targets, and reserve strategies (see
   [`VC/vc-fund-model-reserves`](../vc-fund-model-reserves) for how reserves for follow-on
   capital into apparent winners fit into this).
3. **The VC Method's required ROI makes sense in this context.** A single-deal 15x target
   (see [`VC/vc-method-valuation`](../vc-method-valuation)) isn't naive optimism — it's the
   return math working backward from the reality that most other deals in the same portfolio
   will fail, so the winners need to carry the fund.
4. **"Loss ratio" is a normal, even healthy, fund statistic** — a 40% below-1x rate isn't a
   sign of a bad fund; the concentration curve shows this fund still returned 7.44x gross
   *because of*, not despite, that distribution. A VC fund with a low loss ratio might actually
   indicate insufficient risk-taking to catch true outliers.

## Reading the concentration curve

`output/concentration_curve.png` plots cumulative % of proceeds against cumulative % of deals
(ranked best to worst) — the further this curve bows away from the diagonal "equal
contribution" line, the more power-law-concentrated the portfolio's returns are. A perfectly
even portfolio (every deal contributing proportionally) would trace the diagonal exactly; this
project's curve reaches 86% of total value from just the top 25% of deals — a strongly
concentrated, realistically power-law-shaped outcome.
