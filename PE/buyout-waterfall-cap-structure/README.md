# Buyout Capital Structure & Return Waterfall

Models a buyout equity structure — sponsor participating preferred, sponsor common,
management rollover, and a management option pool — for a hypothetical B2B services company
("Ironclad Security Systems"), and runs simplified exit proceeds through the distribution
waterfall to show exactly how much each equity class actually realizes.

For the theory behind the structure and the waterfall mechanics, see
[`theory/buyout_waterfall.md`](theory/buyout_waterfall.md).

## What the code does

1. **Builds the capital structure** ([`data/deal_assumptions.csv`](data/deal_assumptions.csv))
   — computes Entry EV, debt, and total equity required, then splits sponsor equity into
   preferred (90%) and common (10%), sizes management rollover and the option pool
   (10% of fully diluted common).
2. **Computes exit equity value** via a simplified LBO (flat % of EBITDA debt paydown,
   same approach as [`PE/lbo-calculator-consumer-products`](../lbo-calculator-consumer-products)).
3. **Runs the exit proceeds through a 3-tier waterfall**: (1) return of preferred capital,
   (2) accrued cumulative preferred return, (3) pro-rata participation in the remainder
   across all classes — including preferred, since it's participating.
4. **Computes MOIC by equity class** to show how the same deal outcome translates into very
   different realized returns depending on which instrument you hold.
5. **Outputs**: a deal summary, waterfall detail CSV, a proceeds-split pie chart, and a
   stacked bar chart showing each class's proceeds by waterfall tier.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs** — a
mechanics demonstration of buyout capital structure and waterfall distribution rather than an
analysis of a real deal.

## How to run

```bash
cd code
pip install -r requirements.txt
python waterfall_model.py
```

Outputs are written to `output/`.

## Folder structure

```
buyout-waterfall-cap-structure/
├── code/
│   ├── waterfall_model.py
│   └── requirements.txt
├── data/
│   └── deal_assumptions.csv
├── theory/
│   └── buyout_waterfall.md
├── output/                  # generated summary, waterfall detail, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- Total equity required: **~$188mm**, split into **Sponsor Preferred (~$156mm, 90%)**,
  **Sponsor Common (~$17mm)**, and **Management Rollover ($15mm)**, plus a **10% option pool**
  granted to management on top.
- At a **$457.7mm exit equity value**, **Sponsor Preferred realizes 2.66x MOIC** — capturing
  its return of capital, its full 8% cumulative compounded preferred return (~$73mm), *and*
  a pro-rata share of the Tier 3 upside since it's participating.
- **Sponsor Common and Management Rollover both realize only ~1.19x MOIC** — they only
  participate in Tier 3, with no seniority or contractual return ahead of them.
- The **Management Option Pool receives ~$4.3mm** on zero invested capital — pure incentive
  compensation, illustrating why option grants are valuable even without a cash investment.
