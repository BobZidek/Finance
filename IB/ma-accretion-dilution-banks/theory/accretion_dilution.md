# M&A Accretion / Dilution Analysis — Theory

## What it is

Accretion/dilution analysis answers a narrow but critical question for a **strategic
acquirer**: *does this deal increase or decrease our earnings per share (EPS)?* It says
nothing about whether the deal creates long-term value (that's what a DCF/synergy NPV
analysis is for) — a deal can be EPS-accretive and still destroy value, or EPS-dilutive
and still be strategically sound. It's a first-pass "gut check" bankers run on almost
every M&A deal because public-company management and shareholders care intensely about
near-term EPS impact.

## Step 1 — Determine the purchase price

```
Offer Price per Share = Target's Pre-Deal Share Price × (1 + Premium)
Total Purchase Price  = Offer Price per Share × Target Diluted Shares Outstanding
```

Premiums in real deals typically run 20-40% over the unaffected share price, compensating
target shareholders for giving up control and the standalone upside they'd otherwise keep.

## Step 2 — Determine the consideration mix

Deals are financed with some mix of **cash** and **acquirer stock**:

- **Cash consideration** is usually funded by new debt (or occasionally excess balance
  sheet cash). New debt carries an interest cost, which reduces pro forma net income
  (after-tax).
- **Stock consideration** requires the acquirer to issue new shares, which dilutes existing
  shareholders by increasing the share count — even before considering earnings impact.

The mix matters enormously for accretion/dilution, which is why every deal is judged
across a Cash% sensitivity range, not just management's chosen structure.

## Step 3 — Combine net income

```
Pro Forma Net Income = Acquirer NI + Target NI
                        + After-Tax Synergies
                        − After-Tax Incremental Interest Expense (on new deal debt)
```

- **Synergies** (cost savings, cross-sell revenue) are typically phased in over 1-3 years
  post-close — a "base case" often assumes a conservative run-rate, since overpromising
  synergies is one of the most common ways M&A deals disappoint.
- **Incremental interest expense** is calculated after-tax, since interest is
  tax-deductible.
- A full model would also include incremental D&A from purchase-accounting write-ups of
  target assets to fair value — this project simplifies that away (see `ENHANCEMENTS.md`).

## Step 4 — Combine share count and compute pro forma EPS

```
Pro Forma Diluted Shares = Acquirer Diluted Shares + New Shares Issued (stock consideration)
Pro Forma EPS = Pro Forma Net Income / Pro Forma Diluted Shares
Accretion / (Dilution) % = Pro Forma EPS / Acquirer Standalone EPS − 1
```

## The core intuition: relative P/E and cost of financing

A rough rule of thumb: **an all-stock deal is accretive when the acquirer's P/E is higher
than the target's (effective, post-premium) P/E** — because the acquirer is "buying" earnings
more cheaply (in P/E terms) than its own stock is priced. A **cash deal is accretive whenever
the target's earnings yield (Net Income / Purchase Price) exceeds the after-tax cost of the
debt used to fund it** — the acquired earnings cost less than the financing cost.

That second dynamic shows up directly in this project's output: even with **zero (or
slightly negative) synergies**, the deal is still EPS-accretive, because the target's implied
earnings yield on the purchase price comfortably exceeds the after-tax cost of the new debt.
Higher cash mix is more accretive than higher stock mix here for exactly that reason — debt is
"cheaper" than issuing acquirer stock at the acquirer's current multiple.

## Why accretion/dilution isn't the full story

- It ignores the **premium paid relative to intrinsic/DCF value** — a deal can be accretive
  and still overpay.
- It ignores **balance sheet risk** — leverage from new debt raises the acquirer's risk
  profile even if EPS goes up.
- It's a **near-term (year 1) snapshot** — synergy ramp and integration risk unfold over
  multiple years, so year-1 accretion doesn't guarantee durable accretion.

That's why real banker output pairs accretion/dilution with a standalone DCF/comps valuation
of the target (to check the price is fair) and pro forma leverage ratios (to check the balance
sheet can support the deal).
