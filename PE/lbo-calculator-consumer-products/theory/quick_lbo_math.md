# Quick LBO Math — Theory

## Why a "quick" version exists alongside the full model

A full LBO model (see [`IB/lbo-model-healthcare-services`](../../IB/lbo-model-healthcare-services)
or [`PE/full-lbo-model-business-services`](../full-lbo-model-business-services)) builds a
detailed income statement and multi-tranche debt waterfall. That's necessary for underwriting
an actual deal, but it takes time to build. In practice — screening a new deal for the first
time, or in an interview — investors do a **much faster, simplified version** in their head or
on a napkin to sanity-check whether a deal is even worth spending real diligence time on. This
project builds that simplified calculator explicitly, and — critically — **shows exactly what
it's approximating away** relative to the full model.

## The simplification

Instead of modeling revenue → EBITDA → EBIT → interest → taxes → capex → ΔNWC → free cash
flow → debt service (the full model's approach), this calculator assumes debt paydown is a
**flat percentage of EBITDA each year** (30% here):

```
Debt Paydown_t = Paydown% x EBITDA_t
```

This is a reasonable rough proxy — it captures the fact that debt paydown scales with the
business's cash-generating capacity — but it skips interest expense (and its tax shield),
capex, and working capital entirely. **The two models will diverge** whenever a company is
unusually capex-intensive, working-capital-hungry, or highly levered (where interest expense
consumes a large share of EBITDA) — exactly the cases where the extra modeling effort of a
full LBO pays off. For a "quick screen," the approximation is good enough to rule deals in
or out of further diligence.

## Isolating the leverage effect

This project explicitly computes **both** the levered return and what the same deal would
return with **100% equity financing** (no debt at all):

```
Unlevered MOIC = Exit EV / Entry EV
Levered MOIC = Exit Equity / Entry (Sponsor) Equity
```

The gap between the two IRRs is the **pure leverage contribution** — in the base case here,
leverage turns a 6.0% unlevered IRR into a 16.7% levered IRR, a ~10.7 percentage point boost.
This is the core mechanical reason LBOs exist as a strategy: debt is (usually) cheaper than
the required return on equity, and using more of it concentrates the same underlying business
performance into a smaller equity check — amplifying the return on that equity, for better or
worse (leverage amplifies losses on a bad deal exactly as it amplifies gains on a good one).

## Reading the sensitivity grid

Because this calculator runs in milliseconds, it's cheap to sweep a full Entry × Exit multiple
grid instantly — useful for quickly answering "how much can we afford to overpay and still hit
our return target?" or "how much multiple compression can this deal absorb?" before committing
to build the full model.
