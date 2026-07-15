# Deal Screening Scorecard — Multi-Sector Target Universe

Ranks 10 hypothetical acquisition targets across sectors on a weighted composite score
(growth, margin, leverage, FCF conversion, customer concentration risk), using standardized
z-scores so metrics on different scales can be combined into one ranking.

For the theory behind the methodology, see [`theory/deal_screening_methodology.md`](theory/deal_screening_methodology.md).

## What the code does

1. **Loads the target universe** ([`data/target_universe.csv`](data/target_universe.csv)) —
   10 companies across 10 sectors with revenue growth, EBITDA margin, leverage (Net
   Debt/EBITDA), FCF conversion, and customer concentration.
2. **Loads scoring weights** ([`data/scoring_weights.csv`](data/scoring_weights.csv)) — each
   metric's weight and whether higher values are better (leverage and customer concentration
   are "lower is better").
3. **Standardizes every metric to a z-score** across the universe, flipping the sign for
   "lower is better" metrics.
4. **Computes a weighted composite score** per company and ranks the universe.
5. **Outputs**: the full ranked scorecard CSV, a shortlist summary text file, a ranking bar
   chart, and a per-factor score breakdown chart showing *why* each company scored the way
   it did.

## Data note

All companies and financials are **fictional/illustrative** — a mechanics demonstration
of the screening methodology rather than commentary on real companies. Swap in a real
sourced target universe to make this an actual screening tool.

## How to run

```bash
cd code
pip install -r requirements.txt
python screening_model.py
```

Outputs are written to `output/`.

## Folder structure

```
deal-screening-scorecard/
├── code/
│   ├── screening_model.py
│   └── requirements.txt
├── data/
│   ├── target_universe.csv
│   └── scoring_weights.csv
├── theory/
│   └── deal_screening_methodology.md
├── output/                  # generated scorecard, shortlist, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- **Top 3 shortlist: Clearwater Pool Services, Coastal Marina Management, Vantage Industrial
  Coatings** — all combine above-average growth or margin with below-average leverage.
- **Summit Freight Solutions ranks last** — the combination of the lowest growth (4%),
  lowest margin (10%), highest leverage (3.2x), and highest customer concentration (22%) in
  the universe compounds across every weighted factor.
- The score breakdown chart shows the #1 and #2 targets got there through **different
  factor mixes** — Clearwater leads on growth/FCF conversion/low customer concentration,
  while Coastal Marina leads on margin/FCF conversion despite more moderate growth — a
  reminder that the composite rank alone doesn't tell the full story.
