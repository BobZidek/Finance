# Merger Model with Synergies — Airlines

A 3-year pro forma merger model for a hypothetical stock + cash airline merger
("Continental Skyways" acquiring "Pacific Crest Airlines"), with separately-modeled cost
and revenue synergy ramps, multi-year EPS accretion/dilution, and pro forma leverage.

For the theory behind each step, see [`theory/merger_model_with_synergies.md`](theory/merger_model_with_synergies.md).

**Note:** both airlines are fictional/hypothetical — this project is a mechanics
demonstration, not commentary on any real airline or real M&A activity.

## What the code does

1. **Loads deal assumptions** ([`data/deal_assumptions.csv`](data/deal_assumptions.csv)) —
   acquirer/target financials, premium, cash/stock mix, financing rate, tax rate, cost and
   revenue synergy run-rates, integration costs.
2. **Loads the synergy ramp** ([`data/synergy_ramp.csv`](data/synergy_ramp.csv)) — the % of
   run-rate cost synergies, revenue synergies, and integration costs realized in each of the
   3 years post-close.
3. **Computes deal structure**: purchase equity value, cash/stock split, new shares issued,
   new deal debt.
4. **Builds the 3-year pro forma**: combined EBIT/EBITDA with ramping synergies (revenue
   synergies at a reduced flow-through margin), combined interest expense, pro forma net
   income, pro forma EPS, accretion/dilution %, and pro forma leverage (Net Debt/EBITDA)
   each year.
5. **Builds a sensitivity matrix**: Year-3 accretion/dilution % across a Synergy Realization
   (50%-150% of plan) × Cash Mix (0%-100%) grid.
6. **Outputs**: a deal summary, full 3-year pro forma CSV, sensitivity matrix CSV, an EPS
   accretion chart, a leverage chart, and a sensitivity heatmap.

## Data note

Both companies are **fictional** and all financials are **illustrative, hand-set inputs**.
The mechanics mirror a real merger model exactly; swap in real acquirer/target financials
and diligence-based synergy estimates to make this an actual analysis.

## How to run

```bash
cd code
pip install -r requirements.txt
python merger_model.py
```

Outputs are written to `output/`.

## Folder structure

```
merger-model-airlines/
├── code/
│   ├── merger_model.py
│   └── requirements.txt
├── data/
│   ├── deal_assumptions.csv
│   └── synergy_ramp.csv
├── theory/
│   └── merger_model_with_synergies.md
├── output/                  # generated summary, pro forma, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **$2,223mm purchase equity value** (30% premium, 40% cash / 60% stock), funding
  $889mm of new debt and issuing 41.7mm new acquirer shares.
- Accretion builds from **+9.3% in Year 1 to +21.1% in Year 3** as cost synergies ramp to
  100% of the $220mm run-rate and revenue synergies ramp to 70% of their (haircut) run-rate.
- **Pro forma leverage falls from ~2.67x to ~2.55x** over the 3-year forecast from EBITDA
  growth alone, even with no debt paydown modeled.
- The sensitivity grid shows the deal is **accretive in every single scenario tested** —
  even at only 50% synergy realization and 0% cash consideration (the most conservative
  combination), Year-3 accretion is still +9.1% — indicating the deal's economics don't
  depend on hitting the full synergy target to be earnings-positive.
