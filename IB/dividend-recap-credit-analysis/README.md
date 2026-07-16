# Dividend Recapitalization & Credit Analysis — Crestline Media Networks

Models a mid-hold leveraged dividend recapitalization for a hypothetical PE-owned media
company: pre/post-recap credit metrics mapped to an approximate credit rating band via a
simplified scorecard, and a sponsor IRR/MOIC comparison between the "with recap" and "without
recap" (counterfactual) paths to the same exit — with paydown capacity correctly reduced by
the new tranche's higher interest burden.

For the theory behind dividend recaps and **a real modeling issue this project's own
development caught and fixed**, see
[`theory/dividend_recap_and_credit.md`](theory/dividend_recap_and_credit.md).

## What the code does

1. **Loads recap assumptions** ([`data/recap_assumptions.csv`](data/recap_assumptions.csv))
   — pre-recap capital structure, new debt/dividend terms, FCF conversion assumption, and exit assumptions.
2. **Computes pre- and post-recap credit metrics**: leverage (Debt/EBITDA), interest coverage
   (EBITDA/Interest), and maps each to an approximate credit rating band via a simplified,
   "weakest-link" scorecard.
3. **Projects debt paydown to exit under two scenarios** — with the recap (higher debt, higher
   blended rate) and without it (counterfactual) — with paydown capacity correctly computed as
   FCF **net of interest expense**, so the recap's higher interest burden genuinely slows
   deleveraging rather than being ignored.
4. **Computes sponsor IRR and MOIC** for both scenarios via a bisection-search IRR solver on
   the full multi-date cash flow series (entry, interim dividend if applicable, exit proceeds).
5. **Outputs**: a credit metrics CSV and chart, a sponsor returns comparison CSV, a summary
   text file, and a returns comparison chart.

## Data note

The company and all financial terms are **fictional/illustrative** — a mechanics
demonstration of dividend recap and credit analysis rather than an analysis of a real
transaction.

## How to run

```bash
cd code
pip install -r requirements.txt
python dividend_recap_model.py
```

Outputs are written to `output/`.

## Folder structure

```
dividend-recap-credit-analysis/
├── code/
│   ├── dividend_recap_model.py
│   └── requirements.txt
├── data/
│   └── recap_assumptions.csv
├── theory/
│   └── dividend_recap_and_credit.md
├── output/                  # generated credit metrics, returns comparison, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Credit rating implied to fall from B+/B to B-/CCC+** — leverage rises from 3.61x to 5.00x,
  interest coverage falls from 3.46x to 2.38x.
- **MOIC falls from 4.26x (no recap) to 4.02x (with recap)** — the new tranche's higher
  interest burden compounds over the remaining hold, more than offsetting the $250mm dividend received.
- **IRR rises from 33.6% (no recap) to 40.1% (with recap)** — receiving cash earlier
  meaningfully boosts the annualized return metric even though total dollar proceeds are lower.
- **This is a genuine MOIC-vs-IRR tension**, not a modeling artifact — an earlier version of
  this project's debt paydown logic ignored the extra interest burden entirely and produced an
  implausibly "clean" result (identical total proceeds either way); fixing it to make paydown
  capacity genuinely FCF-based (net of interest) revealed the real trade-off.
