# Asset-Based Lending Borrowing Base Model — Ferrous Metals Distribution Co.

Builds a revolving credit facility borrowing base from the lender's perspective for a
hypothetical industrial distributor — eligible accounts receivable and inventory (net of
ineligibles, at NOLV, with advance rates), reserves, and a springing minimum-availability
covenant check — plus a working-capital stress test.

For the theory behind ABL lending and why it differs fundamentally from cash-flow-based
lending, see [`theory/abl_borrowing_base_theory.md`](theory/abl_borrowing_base_theory.md).

## What the code does

1. **Loads borrowing base assumptions** ([`data/borrowing_base_assumptions.csv`](data/borrowing_base_assumptions.csv))
   — gross AR/inventory, ineligibles, advance rates, NOLV%, reserves, facility commitment,
   outstanding draws/LCs, and the springing covenant threshold.
2. **Computes the AR component**: eligible AR (gross less ineligibles) × advance rate.
3. **Computes the inventory component**: eligible inventory at cost → at NOLV → × advance rate
   (a two-layer haircut).
4. **Computes Net Borrowing Base, Availability** (lesser of borrowing base or facility
   commitment), and **Excess Availability** (availability less draws and LCs).
5. **Checks the springing covenant**: whether Excess Availability has fallen below the
   specified threshold.
6. **Runs a working capital stress test**: 4 scenarios from base case to severe stress,
   showing how Excess Availability (and covenant status) deteriorate.
7. **Outputs**: a summary text file, stress test CSV, a borrowing base bridge chart, and a
   stress test chart.

## Data note

The borrower and all financial data are **fictional/illustrative** — a mechanics
demonstration of ABL borrowing base construction rather than an analysis of a real facility.

## How to run

```bash
cd code
pip install -r requirements.txt
python borrowing_base_model.py
```

Outputs are written to `output/`.

## Folder structure

```
asset-based-lending-borrowing-base/
├── code/
│   ├── borrowing_base_model.py
│   └── requirements.txt
├── data/
│   └── borrowing_base_assumptions.csv
├── theory/
│   └── abl_borrowing_base_theory.md
├── output/                  # generated summary, stress test, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Net Borrowing Base: $57.82mm** ($35.7mm AR component + $24.62mm inventory component, less
  $2.5mm reserves) — below the **$75mm facility commitment**, so the borrowing base (not the
  facility ceiling) is the binding constraint.
- **Excess Availability: $22.82mm**, comfortably above the **$7.5mm springing covenant
  threshold** — the covenant isn't currently live.
- **The stress test shows a real but not unlimited cushion**: the covenant stays untriggered
  through a "Moderate Downturn" scenario (-20% AR, -15% inventory, $10.45mm excess
  availability), but **trips under "Severe Stress" (-35% AR, -25% inventory)**, where excess
  availability falls to just $1.52mm.
