# Merger Model with Synergies — Theory

## How this extends basic accretion/dilution

[`IB/ma-accretion-dilution-banks`](../ma-accretion-dilution-banks) builds a single-year,
static accretion/dilution calculation. A full **merger model** extends that in three ways,
all present here:

1. **Multi-year projection** — synergies rarely arrive on day one; a real model shows how
   accretion/dilution evolves year by year as synergies ramp up.
2. **Cost *and* revenue synergies, modeled separately** — with different realization curves
   and different credibility.
3. **Pro forma capital structure metrics** (leverage), not just EPS — a strategic buyer's
   board cares about balance sheet impact alongside earnings impact, especially in a
   capital-intensive, cyclical industry like airlines.

## Cost synergies vs. revenue synergies

- **Cost synergies** (headcount overlap, duplicate facilities/systems, combined fleet/
  maintenance contracts, procurement scale) are modeled with **high flow-through** (near
  100% — cost saved is cost saved) and ramp fastest, since they're largely within
  management's direct control to execute.
- **Revenue synergies** (combined route network, connecting traffic, shared loyalty
  program, cross-selling) are inherently less certain — they depend on customer behavior
  and competitive response, not just internal execution. Two standard modeling
  conventions reflect that: (1) a **slower realization ramp** (10% → 40% → 70% here, vs.
  cost synergies at 40% → 75% → 100%), and (2) a **flow-through margin below 100%**
  (80% here) applied to revenue synergies before they hit EBIT, since incremental revenue
  still carries some incremental cost. Many banks go further and **exclude revenue
  synergies from official deal-approval projections entirely**, treating them as
  "upside" rather than underwritten value — worth noting when presenting this kind of
  analysis, since overcrediting revenue synergies is one of the most common ways real
  M&A deals disappoint post-close.

## One-time integration costs — why they're excluded from recurring EPS

Restructuring charges, system migration costs, and severance are **real cash costs** but
are one-time and non-recurring by nature. They're reported (see `output/merger_summary.txt`)
but deliberately **excluded from the recurring pro forma EPS** figures used for the
accretion/dilution conclusion — mixing them in would understate the deal's steady-state
earnings power. They still matter for near-term cash flow and covenant headroom, which is
why they're tracked separately rather than ignored.

## Pro forma leverage — why it matters for a strategic deal

```
Pro Forma Leverage = Combined Net Debt / Combined EBITDA
```

Airlines are unusually debt-intensive (aircraft financing, historically thin margins,
cyclical revenue), so acquirers and rating agencies watch pro forma leverage closely after
any M&A deal — a downgrade risk from added leverage can raise the cost of debt across the
*entire* combined balance sheet, not just the new deal debt, which would silently erode
the EPS accretion the deal appeared to create. In this model, leverage falls from ~2.75x at
close to ~2.55x by Year 3 purely from EBITDA growth (no debt paydown is modeled here — see
`ENHANCEMENTS.md`), which is the kind of trajectory a ratings-sensitive acquirer wants to see.

## Reading the sensitivity grid

The Synergy Realization × Cash Mix grid answers two separate risk questions at once:
- **Execution risk** (rows): what if synergies come in at only 50% of run-rate — or overshoot
  at 150%?
- **Financing risk** (columns): how does the deal's accretion profile change with more/less
  cash (debt-funded) vs. stock consideration?

Note that **even at only 50% synergy realization and 0% cash (all-stock)**, the deal is still
Year-3 accretive (+9.1%) — meaning the deal doesn't *depend* on synergies to work, which is a
materially stronger underwriting case than one where the entire accretion thesis rests on
hitting 100%+ of a synergy target.
