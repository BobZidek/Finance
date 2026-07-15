# Market Sizing (TAM/SAM/SOM) — Vector Database & AI Retrieval Infrastructure

Builds a top-down AND bottom-up TAM estimate for an emerging market category (vector
databases and AI retrieval infrastructure), triangulates between the two, derives SAM and
SOM, projects a 5-year growth trajectory, and maps the competitive landscape.

For the theory behind TAM/SAM/SOM methodology and the full investment thesis reasoning, see
[`theory/market_sizing_and_thesis.md`](theory/market_sizing_and_thesis.md).

## What the code does

1. **Loads market sizing assumptions** ([`data/market_sizing_assumptions.csv`](data/market_sizing_assumptions.csv))
   — both a top-down input set (global enterprise software spend × category attribution %)
   and a bottom-up input set (target enterprise count × average spend per enterprise), plus
   growth rates, SAM %, and SOM % assumptions.
2. **Projects both TAM estimates over 5 years**, growing each independently at its own rate.
3. **Computes a midpoint TAM** (simple average of the two methods) and derives **SAM** (a %
   of midpoint TAM) and **SOM** (a % of Year-5 SAM, calibrated to a realistic single-company
   obtainable share).
4. **Loads a 5-category competitive landscape** ([`data/competitive_landscape.csv`](data/competitive_landscape.csv))
   with strengths, weaknesses, and threat level for each.
5. **Outputs**: the full TAM/SAM/SOM projection CSV, competitive landscape CSV, a market
   sizing summary text file, a TAM triangulation chart (top-down vs. bottom-up vs. midpoint),
   and a TAM/SAM/SOM bar chart for the final projection year.

## Data note

All market sizing inputs are **illustrative estimates**, not sourced from a live market
research database (this environment couldn't reach live data sources) — the sector itself
(vector databases / AI retrieval infrastructure) and the competitive category descriptions
are general, well-known market dynamics as of the mid-2020s, not specific claims about any
named company's actual financials or market share.

## How to run

```bash
cd code
pip install -r requirements.txt
python market_sizing_model.py
```

Outputs are written to `output/`.

## Folder structure

```
market-sizing-ai-infra/
├── code/
│   ├── market_sizing_model.py
│   └── requirements.txt
├── data/
│   ├── market_sizing_assumptions.csv
│   └── competitive_landscape.csv
├── theory/
│   └── market_sizing_and_thesis.md
├── output/                  # generated projection, competitive landscape, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Base year (2026) TAM diverges sharply between methods**: **$32.0bn top-down** vs.
  **$7.5bn bottom-up** — over 4x apart, itself the most important finding of the exercise
  (see the theory doc for why this divergence should be reported, not resolved away).
- By **2031, the midpoint TAM reaches $68.9bn**, with a **$24.1bn SAM**.
- **SOM: $241mm** — calibrated to represent a realistic top-decile single-company outcome
  (1% of SAM), not an average expectation.
- The **competitive landscape flags two "High" threat categories** (hyperscaler-native
  offerings and specialized venture-backed startups) — a credible investment thesis needs a
  specific answer to both, not just one.
