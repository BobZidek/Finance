# Value Creation Bridge — Specialty Retail / Building Products

Decomposes sponsor equity value growth for a hypothetical specialty retail / building
products distributor ("Anchor Point Building Supply") into revenue growth, margin expansion,
multiple expansion, deleveraging, and transaction fee drag — with a built-in reconciliation
check confirming the decomposition sums exactly to the actual result.

For the theory behind the decomposition methodology, see
[`theory/value_creation_bridge.md`](theory/value_creation_bridge.md).

## What the code does

1. **Loads deal assumptions** ([`data/deal_assumptions.csv`](data/deal_assumptions.csv)) —
   entry revenue/EBITDA, entry/exit multiples, leverage, revenue growth rate, exit EBITDA
   margin, hold period.
2. **Computes entry and exit Enterprise Value, debt, and equity value** (debt paydown via a
   simplified flat % of EBITDA sweep).
3. **Decomposes the EV change telescopically**: revenue growth (at entry margin/multiple) →
   margin expansion (at exit revenue, entry multiple) → multiple expansion (at exit
   revenue/margin, moving to exit multiple) — each step isolating one lever's contribution.
4. **Adds deleveraging** (entry debt − exit debt, flows directly to equity) and **transaction
   fees** (a drag on entry equity) as the remaining two bridge components.
5. **Verifies reconciliation**: sums all five components and checks the total exactly equals
   the actual entry-to-exit equity value change.
6. **Outputs**: a bridge summary text file (with the reconciliation PASS/FAIL check) and a
   waterfall chart visualizing entry equity → each driver → exit equity.

## Data note

The target is **fictional** and all financials are **illustrative, hand-set inputs** — a
mechanics demonstration of the value creation bridge methodology rather than an analysis of
a real portfolio company.

## How to run

```bash
cd code
pip install -r requirements.txt
python value_bridge_model.py
```

Outputs are written to `output/`.

## Folder structure

```
value-creation-bridge-retail/
├── code/
│   ├── value_bridge_model.py
│   └── requirements.txt
├── data/
│   └── deal_assumptions.csv
├── theory/
│   └── value_creation_bridge.md
├── output/                  # generated bridge summary, waterfall chart
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Entry Equity $139.1mm → Exit Equity $442.6mm** over a 5-year hold — **3.18x MOIC / 26.0% IRR**.
- **Revenue growth is the largest single driver (+$122.4mm)**, followed by **deleveraging
  (+$70.1mm)**, **multiple expansion (+$60.4mm)**, and **margin expansion (+$56.7mm)**, with
  transaction fees a small drag (−$6.1mm).
- **The reconciliation check passes exactly** — the five bridge components sum to precisely
  the actual $303.5mm equity value increase, confirming the decomposition is complete and
  internally consistent rather than an illustrative approximation.
- Over **half of total value creation came from revenue growth and deleveraging combined**
  — levers the sponsor's own operating thesis and financing structure directly controlled —
  rather than depending primarily on multiple expansion, generally viewed as a
  higher-quality, more repeatable return profile.
