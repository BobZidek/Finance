# Football Field Valuation — Athletic Apparel

Combines trading comps, precedent transactions, and a DCF into a single "football field"
chart valuing a hypothetical private athletic apparel brand ("Apex Trailhead Apparel").

For the theory behind each method and how they're synthesized, see
[`theory/football_field_valuation.md`](theory/football_field_valuation.md).

## What the code does

1. **Trading comps**: loads 7 public athletic apparel/footwear peers
   ([`data/trading_comps.csv`](data/trading_comps.csv)), computes EV/EBITDA for each, and
   applies the 25th-75th percentile range to the target's EBITDA.
2. **Precedent transactions**: loads 6 illustrative historical M&A deals in the sector
   ([`data/precedent_transactions.csv`](data/precedent_transactions.csv), with control
   premiums embedded in the multiples) and applies the same percentile approach.
3. **DCF**: builds a 5-year FCF forecast for the target with an EBITDA margin ramping toward
   a terminal margin, discounts at WACC, and computes a Gordon Growth terminal value — with
   a low/high range generated from a WACC ± 0.75% sensitivity band.
4. **Combines all three** into a football field chart (horizontal range bars) and a text
   summary with the overall implied EV and equity value range.

## Data note

All peer, precedent transaction, and target figures are **illustrative** — this environment
couldn't reach live market data (network/SSL restriction). The precedent transactions are
labeled generically ("Deal A", "Deal B", ...) rather than naming real transactions, since
their multiples are approximated rather than sourced from verified deal data. The target
company is fictional. The mechanics mirror a real football field exactly — swap in real
comps, real deal data, and a real target to make this an actual valuation.

## How to run

```bash
cd code
pip install -r requirements.txt
python football_field_model.py
```

Outputs are written to `output/`.

## Folder structure

```
football-field-athletic-apparel/
├── code/
│   ├── football_field_model.py
│   └── requirements.txt
├── data/
│   ├── trading_comps.csv
│   ├── precedent_transactions.csv
│   └── target_and_dcf.csv
├── theory/
│   └── football_field_valuation.md
├── output/                  # generated tables, chart, summary
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- **Trading comps** imply an EV of **$736mm - $1,722mm** — the widest range, reflecting a
  peer set that spans a distressed name (Under Armour) to a high-growth name (On Holding).
- **Precedent transactions** imply **$1,147mm - $1,375mm** — tighter and higher, since
  transaction multiples embed a control premium that trading comps don't.
- **DCF** implies **$785mm - $991mm**, sitting toward the lower end of the trading comps range.
- **Overall implied EV range: $736mm - $1,722mm**; implied **equity value: $586mm - $1,572mm**
  after subtracting the target's $150mm net debt. The precedent-transaction and DCF ranges
  overlap tightly around $900mm-$1,150mm, which is where a banker would likely anchor a
  recommended value — illustrating why you present all three ranges rather than a single number.
