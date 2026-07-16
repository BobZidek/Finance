# Dividend Recapitalization & Credit Analysis — Theory

## What a dividend recap is, and why sponsors do it

A **dividend recapitalization** ("dividend recap") is a mid-hold transaction where a
PE-owned company **raises new debt and uses the proceeds to pay a special dividend to its
equity holders** (the sponsor), without selling the business or changing operations. It lets a
sponsor **realize partial liquidity before the eventual exit** — a genuinely valuable option
when a portfolio company has delevered enough to support additional debt, market conditions for
new debt are favorable, and the fund wants to return capital to LPs (or reduce risk) ahead of a
full sale.

## Credit impact — a real trade-off, not a free lunch

```
Leverage = Total Debt / EBITDA
Coverage = EBITDA / Interest Expense
```

This project's recap **raises leverage from 3.61x to 5.00x** and **drops interest coverage
from 3.46x to 2.38x**, moving the company's implied credit rating band from **B+/B down to
B-/CCC+** on the simplified scorecard used here (a "weakest link" approach: the worse of the
two metrics determines the band, mirroring how rating agencies weight leverage and coverage as
the primary credit drivers for a leveraged issuer). A meaningfully weaker credit profile is a
**real cost** of a dividend recap — even without any operational deterioration, the company
is now more fragile to a downturn, has less cushion before covenant or coverage stress, and
will pay a higher cost of capital on any future refinancing.

## Why this project's paydown model had to account for interest expense explicitly

An earlier version of this project used a flat "X% of EBITDA" debt paydown assumption
(matching the style used in several other LBO projects in this repo) for both the with-recap
and without-recap paths — which produced an implausibly clean result: **total sponsor proceeds
were identical ($1,324.11mm) under both scenarios**, differing only in timing. That's a
red flag, not a coincidence: it meant the model was silently ignoring that the recap's new debt
tranche carries a **higher interest rate (9.5% vs. the original 8.0%) on a larger balance**,
which should genuinely slow deleveraging, not just shift cash flow timing. This project's
paydown logic now correctly computes **available cash for paydown as `EBITDA x FCF conversion %
− interest expense on the beginning-of-year balance`** — so a more heavily levered capital
structure mechanically pays down slower, exactly as it would in reality.

## The result: IRR and MOIC tell genuinely different stories

| | With Recap | Without Recap |
|---|---|---|
| Interim Dividend | $250.0mm | $0.0mm |
| Exit Equity | $1,037.2mm | $1,363.9mm |
| **MOIC** | **4.02x** | **4.26x** |
| **IRR** | **40.1%** | **33.6%** |

**The recap reduces total dollar proceeds (MOIC falls by 0.24x)** — the extra interest expense
on the new tranche is a real, permanent drag that compounds over the remaining hold, more than
offsetting the dividend received. **But the recap increases IRR by 6.4 percentage points**,
because IRR rewards getting cash *earlier* — receiving $250mm in Year 2 rather than waiting
until Year 5 for the equivalent (and more) value meaningfully boosts the annualized return
metric, even though it corresponds to *fewer total dollars* in this case.

## Why this genuinely matters for how a sponsor should decide

This is one of the sharpest real illustrations of the MOIC-vs-IRR tension covered anywhere in
this repo (see also [`PE/full-lbo-model-business-services`](../../PE/full-lbo-model-business-services)
for the same tension in an exit-timing context). A fund that reports and is compensated
primarily on **IRR** (common, especially for funds near the end of their investment period
needing to show strong marks or return capital to LPs on schedule) has a real incentive to
execute this recap even though it reduces total dollar value creation. A fund optimizing purely
for **absolute dollar return to LPs** should be more skeptical. Neither answer is
"more correct" in the abstract — it depends on the fund's own liquidity needs, reporting
incentives, and how much credit deterioration the business (and its lenders) can safely absorb
— which is exactly why real dividend recap decisions get debated at the investment committee
level rather than being a mechanical yes/no from the returns math alone.
