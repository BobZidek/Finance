# Cap Table & Dilution Tracker — Seed through Series C

Tracks a hypothetical startup's fully-diluted cap table from founding through Series C —
2 SAFE notes converting at Series A (cap vs. discount, resolved via an iterative solver), an
option pool top-up at Series A, and straightforward Series B/C priced rounds.

For the theory behind SAFE conversion and the option pool "shuffle," see
[`theory/cap_table_mechanics.md`](theory/cap_table_mechanics.md).

## What the code does

1. **Loads the founding cap table** ([`data/founders_and_pool.csv`](data/founders_and_pool.csv))
   — 2 founders and an initial unallocated option pool.
2. **Loads 2 seed-stage SAFEs** ([`data/safes.csv`](data/safes.csv)) — investment amount,
   valuation cap, and discount for each.
3. **Loads 3 priced rounds** ([`data/priced_rounds.csv`](data/priced_rounds.csv)) — Series A
   (with a 15% post-money option pool top-up), Series B, and Series C.
4. **Resolves SAFE conversion + Series A pricing simultaneously** via a small iterative solver,
   since a SAFE's discount price depends on the very round price its conversion helps set.
5. **Solves the option pool top-up algebraically**, correctly diluting only pre-money holders.
6. **Processes Series B and C** as standard priced rounds (no pool top-up).
7. **Outputs**: the full round-by-round ownership % history, the final post-Series-C cap
   table, a founder dilution line chart, and a stacked ownership-by-round chart.

## Data note

The startup, founders, SAFE investors, and all financial terms are **fictional/illustrative**
— a mechanics demonstration. The SAFE conversion and pool shuffle algebra are exactly correct
and match how real cap table software resolves the same circularity.

## How to run

```bash
cd code
pip install -r requirements.txt
python cap_table_model.py
```

Outputs are written to `output/`.

## Folder structure

```
cap-table-dilution-tracker/
├── code/
│   ├── cap_table_model.py
│   └── requirements.txt
├── data/
│   ├── founders_and_pool.csv
│   ├── safes.csv
│   └── priced_rounds.csv
├── theory/
│   └── cap_table_mechanics.md
├── output/                  # generated cap table history, final table, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Founder ownership falls from 90.9% at founding to 36.1% after Series C** across the four
  financing events.
- **SAFE 1's $8M cap is the binding conversion constraint** (not its 20% discount) — its cap
  price ($0.727/share) beats its discount price (~$0.865/share) at the resulting Series A
  price of $1.08/share.
- The **Series A option pool top-up (to 15% post-money) dilutes founders more than a naive
  calculation would suggest**, since the new pool shares are added pre-money — borne entirely
  by existing holders, not the incoming Series A investor.
- By the final cap table, ownership is spread across **8 distinct holder classes** (2
  founders, 2 SAFE investors, 3 rounds of priced investors, and the option pool) — see
  `output/final_cap_table.csv` for the complete breakdown.
