# Value Creation Bridge — Theory

## What it answers

An LBO returns calculator tells you *how much* a deal returned. A value creation bridge
tells you **why** — decomposing total equity value growth into the specific operational and
financial levers that produced it. This is the standard chart PE firms build for portfolio
reviews, LP reporting, and post-mortems: it turns "we made 3.18x" into "here's exactly where
that came from," which is what actually informs whether the fund's investment thesis worked
as planned.

## The four (plus one) levers

```
Equity Value Growth = Revenue Growth + Margin Expansion + Multiple Expansion
                       + Deleveraging − Transaction Fees
```

1. **Revenue Growth** — value created purely from the business getting bigger, holding
   margin and multiple constant at their entry levels. Isolated by asking: "if margin and
   multiple had never changed, how much would EV have grown just from revenue growth
   flowing through the entry EBITDA margin?"
2. **Margin Expansion** — value created from the business becoming more profitable per
   dollar of (now-larger) revenue, holding the multiple constant. Isolated as the *next*
   incremental step: apply the actual exit margin to the actual exit revenue, still at the
   entry multiple.
3. **Multiple Expansion** — value created purely from the market paying more per dollar of
   EBITDA at exit than the sponsor paid at entry (or destroyed, if the multiple compresses).
   This is the only lever driven by market sentiment/timing rather than operational execution.
4. **Deleveraging** — every dollar of debt paid down over the hold period flows dollar-for-
   dollar to the equity holder at exit, *independent of any change in Enterprise Value at
   all*. This is why a flat-EV, flat-EBITDA, flat-multiple deal can still return meaningfully
   above 1.0x MOIC — pure debt paydown is a real return driver on its own.
5. **Transaction Fees** — a real drag on entry equity (the sponsor pays more into the deal
   than the deal's own EV would otherwise require), included here as a small negative bucket.

## Why the order matters (it's a telescoping decomposition, not independent buckets)

The revenue growth and margin expansion contributions are calculated in a specific
**sequence** — revenue growth first (at the entry margin), then margin expansion (moving
from entry margin to exit margin, at the now-larger exit revenue). This isn't arbitrary:
because revenue and margin both changed simultaneously in reality, there's no unique way to
split "how much of the EBITDA growth was revenue vs. margin" without picking an order to
attribute the *interaction* between the two changes. This project attributes the
revenue-times-margin interaction effect to the margin expansion bucket (by holding revenue at
its *exit* level when isolating margin's contribution) — a standard, defensible convention,
but worth stating explicitly rather than leaving implicit, since a different convention
(attributing the interaction to revenue growth instead) would shift dollars between the two
buckets without changing the total.

## The reconciliation check

The code explicitly verifies that **the sum of all five bridge components exactly equals**
the actual entry-to-exit equity value change (`output/bridge_summary.txt` reports PASS/FAIL).
This isn't cosmetic — a bridge that doesn't reconcile to the actual number is actively
misleading, since it implies the four levers explain 100% of the outcome when in fact some
unexplained residual exists. Building the check in is what makes this a trustworthy analytical
tool rather than a chart that merely *looks* rigorous.

## Reading this project's result

In this run, **revenue growth is the single largest driver ($122.4mm)**, followed by
**deleveraging ($70.1mm)**, **multiple expansion ($60.4mm)**, and **margin expansion
($56.7mm)**, with transaction fees a small drag (−$6.1mm). A sponsor reviewing this bridge
would note: over half the total value creation (revenue growth + deleveraging, ~$192mm of
$303mm) came from levers the sponsor's own operational thesis and financing structure
directly controlled, rather than depending on multiple expansion (market timing) — generally
read as a *higher-quality*, more repeatable source of returns than a deal that relied
primarily on paying a low multiple and hoping to sell at a higher one.
