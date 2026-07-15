# Multi-Sector Comps Dashboard — Software / SaaS

Regresses EV/Revenue against revenue growth across a 13-company SaaS peer set, flags each
peer as over/under/fairly valued relative to the regression line, and applies the
growth-adjusted multiple to a hypothetical private target — compared directly against the
naive flat-median-multiple approach from the fast-food comps project.

For the theory behind the regression approach, see [`theory/regression_based_comps.md`](theory/regression_based_comps.md).

## What the code does

1. **Loads peer data** ([`data/saas_peers.csv`](data/saas_peers.csv)) — EV, revenue, YoY
   revenue growth, and FCF margin for 13 public SaaS companies. Attempts a live data
   refresh via `yfinance` first, falling back to the static snapshot (see data note).
2. **Computes EV/Revenue and Rule of 40 score** (growth % + FCF margin %) for each peer.
3. **Runs an OLS regression** of EV/Revenue on revenue growth across the peer set, computing
   R² and each peer's residual from the fitted line.
4. **Flags each peer** as Overvalued / Undervalued / Fairly Valued based on whether its
   residual exceeds ±0.5 standard deviations.
5. **Applies the regression to the target's growth rate** ([`data/target_company.csv`](data/target_company.csv))
   to derive a growth-adjusted implied EV/Revenue multiple, and compares it against a flat
   median-multiple approach.
6. **Outputs**: the full peer dashboard CSV, a regression summary text file, a growth-vs-
   multiple scatter plot with the regression line and target overlay, and a Rule of 40 bar chart.

## Data note

Peer and target financials are **illustrative, hand-curated approximate figures** — this
environment couldn't reach live market data (network/SSL restriction). The code includes a
live-data code path (`yfinance`) that's currently disabled with a clear log message and
falls back to the static CSV — see [`ENHANCEMENTS.md`](ENHANCEMENTS.md) for wiring it up
against a reachable data source.

## How to run

```bash
cd code
pip install -r requirements.txt
python comps_dashboard.py
```

Outputs are written to `output/`.

## Folder structure

```
comps-dashboard-saas/
├── code/
│   ├── comps_dashboard.py
│   └── requirements.txt
├── data/
│   ├── saas_peers.csv
│   └── target_company.csv
├── theory/
│   └── regression_based_comps.md
├── output/                  # generated dashboard, regression summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- The regression **EV/Revenue = 2.16 + 52.31 × Growth** fits the peer set with **R² = 0.64** —
  growth alone explains roughly two-thirds of the multiple dispersion across this peer set.
- **CrowdStrike (+2.67) and ServiceNow (+4.80)** screen as the most overvalued relative to
  their growth rate; **Zscaler (−2.54), Snowflake (−2.53), and Atlassian (−3.06)** screen as
  the most undervalued.
- For the target (20% growth), the **growth-adjusted regression multiple (12.62x) implies an
  EV about 20% higher** than the flat peer-median multiple (10.48x) — a material difference
  that a flat-median comps approach would have missed entirely, since the target grows faster
  than the median peer in the set.
