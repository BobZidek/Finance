# M&A Accretion / Dilution Calculator — Regional Banks

Models a hypothetical stock + cash acquisition between two fictional regional banks
("Meridian Bancorp" acquiring "Heritage State Bank") to determine whether the deal is
EPS-accretive or dilutive to the acquirer, and how sensitive that outcome is to the
consideration mix and premium paid.

For the theory behind each step, see [`theory/accretion_dilution.md`](theory/accretion_dilution.md).

**Note:** both companies are fictional/hypothetical — this project is a mechanics
demonstration, not a real deal analysis. See the data note below.

## What the code does

1. **Loads deal assumptions** from [`data/deal_assumptions.csv`](data/deal_assumptions.csv) —
   acquirer/target financials, premium, cash/stock mix, financing rate, tax rate, synergies.
2. **Computes the purchase price** and splits it into cash and stock consideration.
3. **Computes new shares issued** (stock portion ÷ acquirer share price) and **new debt**
   (cash portion, assumed 100% debt-financed).
4. **Builds pro forma net income**: combined NI + after-tax synergies − after-tax
   incremental interest expense on the new debt.
5. **Computes pro forma EPS** and the **accretion/(dilution) %** vs. acquirer standalone EPS.
6. **Builds a sensitivity matrix**: accretion/dilution % across a Cash Mix (0-100%) ×
   Premium (10-40%) grid.
7. **Solves for break-even synergies** — the annual pre-tax synergies at which the deal is
   exactly EPS-neutral (via binary search).
8. **Outputs**: a deal summary text file, sensitivity matrix CSV, an EPS comparison chart,
   and a sensitivity heatmap.

## Data note

Both companies are **fictional** and all financials are **illustrative, hand-set inputs**
— this deliberately avoids implying commentary on any real bank or real M&A activity. The
mechanics, however, mirror a real accretion/dilution model exactly; swap in real acquirer/
target financials from public filings to turn this into an analysis of an actual deal.

## How to run

```bash
cd code
pip install -r requirements.txt
python ma_model.py
```

Outputs are written to `output/`.

## Folder structure

```
ma-accretion-dilution-banks/
├── code/
│   ├── ma_model.py          # main analysis script
│   └── requirements.txt
├── data/
│   └── deal_assumptions.csv # acquirer/target financials, deal terms
├── theory/
│   └── accretion_dilution.md
├── output/                  # generated summary, sensitivity matrix, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- At a **25% premium, 50/50 cash-stock split**, the deal is **+6.2% accretive**
  ($3.00 standalone EPS → $3.19 pro forma EPS).
- **Break-even pre-tax synergies are actually negative (≈ −$6.5mm)** — meaning the deal
  would still be accretive even with *zero* synergies. This is the classic cash-deal dynamic:
  the target's earnings yield on the purchase price exceeds the after-tax cost of the new
  debt, so the deal "pays for itself" on financing terms alone, before any operational
  synergies are realized.
- The sensitivity matrix shows accretion ranging from **+0.8% (40% premium, all-stock)** to
  **+12.0% (10% premium, all-cash)** — cash-funded deals are meaningfully more accretive
  than stock-funded ones here, and accretion decreases monotonically as the premium paid
  rises, exactly as the theory predicts.
