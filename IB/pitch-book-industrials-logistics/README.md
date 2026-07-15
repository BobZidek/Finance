# Full Pitch Book — Industrials / Logistics

The capstone IB project: combines **four** valuation methodologies — trading comps, precedent
transactions, a DCF, and an LBO "ability-to-pay" analysis — into a single football field for a
hypothetical private 3PL / freight brokerage and warehousing target ("Vanguard Logistics
Solutions"), plus a written recommendation.

For the full pitch book structure and the theory behind the ability-to-pay analysis, see
[`theory/pitch_book_structure.md`](theory/pitch_book_structure.md).

## What the code does

1. **Trading comps**: 7 public logistics/transportation peers
   ([`data/trading_comps.csv`](data/trading_comps.csv)) → EV/EBITDA 25th-75th percentile
   range applied to the target.
2. **Precedent transactions**: 5 illustrative historical logistics M&A deals
   ([`data/precedent_transactions.csv`](data/precedent_transactions.csv), control premiums
   embedded) → same percentile approach.
3. **DCF**: 5-year FCF forecast with EBITDA margin ramping to a terminal margin, discounted
   at WACC with a Gordon Growth terminal value, ranged over a WACC ± 0.75% band.
4. **LBO Ability-to-Pay** (new methodology, not used in earlier projects): binary-searches
   for the maximum entry multiple a financial sponsor could pay and still clear a 22% IRR
   target over a 5-year hold (± 2% for a conservative/aggressive sponsor range), using the
   same debt-schedule engine as [`IB/lbo-model-healthcare-services`](../lbo-model-healthcare-services).
5. **Combines all four** into a football field chart and a written recommendation
   (`output/recommendation.txt`) proposing where the range should anchor and why.

All assumptions live in [`data/target_assumptions.csv`](data/target_assumptions.csv).

## Data note

All peer, precedent transaction, and target figures are **illustrative** — this environment
couldn't reach live market data (network/SSL restriction). Precedent transactions are labeled
generically ("Deal A", "Deal B", ...) rather than naming real deals. The target is fictional.
The mechanics mirror a real pitch book valuation workup exactly; swap in real comps, real deal
data, and a real target to make this an actual analysis.

## How to run

```bash
cd code
pip install -r requirements.txt
python pitch_book.py
```

Outputs are written to `output/`.

## Folder structure

```
pitch-book-industrials-logistics/
├── code/
│   ├── pitch_book.py
│   └── requirements.txt
├── data/
│   ├── trading_comps.csv
│   ├── precedent_transactions.csv
│   └── target_assumptions.csv
├── theory/
│   └── pitch_book_structure.md
├── output/                  # generated tables, football field chart, recommendation
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

| Methodology | Implied EV Range | Midpoint |
|---|---|---|
| Trading Comps | $1,484mm - $2,040mm | $1,999mm |
| Precedent Transactions | $1,029mm - $1,239mm | $1,102mm |
| DCF | $1,070mm - $1,361mm | $1,199mm |
| LBO Ability-to-Pay | $854mm - $1,018mm | $923mm |

- **LBO ability-to-pay sits lowest across all four methods** — a financial sponsor can't pay
  for synergies the way a strategic acquirer can, so its maximum supportable price is
  structurally below what a strategic (implicit in precedent transactions and trading comps)
  could justify. This is exactly the pattern real pitch books expect to see.
- **Trading comps produce the widest, highest range** — the public peer set mixes an
  asset-light freight brokerage (C.H. Robinson) with asset-heavy carriers (Old Dominion,
  Saia), which trade at structurally different multiples.
- The **core recommended range is $1,070mm-$1,239mm** — the overlap of DCF and precedent
  transactions, the two most target-specific methods — treating trading comps as a sanity
  check rather than the primary driver of the recommendation.
- The **LBO ability-to-pay ceiling ($1,018mm) sits just below that core range**, implying
  financial sponsors are likely priced out of a process anchored there — a concrete, code-derived
  reason to recommend a targeted strategic-buyer process over a broad auction (see
  `output/recommendation.txt`).
