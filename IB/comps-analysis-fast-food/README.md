# Comparable Company Analysis — Fast Food / QSR Sector

A trading comps model that values a hypothetical private fast-food chain by benchmarking it
against seven public peers (MCD, YUM, QSR, WEN, SHAK, DPZ, CMG).

For the theory behind each step, see [`theory/comparable_company_analysis.md`](theory/comparable_company_analysis.md).

## What the code does

1. **Loads peer financials** from [`data/fast_food_comps.csv`](data/fast_food_comps.csv) — price,
   shares outstanding, debt, cash, revenue, EBITDA, EBIT, net income, EPS.
2. **Computes Enterprise Value** for each peer: `Market Cap + Debt + Minority Interest + Preferred − Cash`.
3. **Computes trading multiples**: EV/Revenue, EV/EBITDA, EV/EBIT, P/E, and EBITDA margin.
4. **Summarizes the peer set**: mean, median, min, max, 25th/75th percentile for each multiple.
5. **Applies the multiple range** to a hypothetical private target
   ([`data/target_company.csv`](data/target_company.csv)) to derive an implied Enterprise
   Value and implied Equity Value range (25th percentile / median / 75th percentile).
6. **Outputs**: a comp table, summary stats, implied valuation table (all CSV), and two charts —
   a peer EV/EBITDA bar chart and a valuation-range chart for the target.

## Data note

Peer financials are **illustrative, hand-curated approximate figures** (not a live feed) —
this environment couldn't reach live market data APIs (network/SSL restriction), so the
model is built to run entirely offline against a versioned CSV snapshot. The code is
structured so `data/fast_food_comps.csv` can be swapped for a live pull (see
[`ENHANCEMENTS.md`](ENHANCEMENTS.md)) without touching the analysis logic.

## How to run

```bash
cd code
pip install -r requirements.txt
python comps_model.py
```

Outputs are written to `output/`.

## Folder structure

```
comps-analysis-fast-food/
├── code/
│   ├── comps_model.py       # main analysis script
│   └── requirements.txt
├── data/
│   ├── fast_food_comps.csv  # peer group financials
│   └── target_company.csv   # hypothetical private target
├── theory/
│   └── comparable_company_analysis.md
├── output/                  # generated tables + charts (run the script to populate)
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- Peer set **median EV/EBITDA ≈ 20.2x**, ranging from Wendy's (~11.6x) to Shake Shack (~33.3x) —
  the spread reflects growth expectations and franchised vs. company-operated mix more than
  current profitability.
- **Mean P/E (49.3x) vs. median P/E (28.7x)** diverge sharply because Shake Shack's thin LTM
  net income produces a ~173x outlier multiple — a concrete example of why medians (not
  means) anchor a comps range.
- Applying the peer EV/EBITDA range to the hypothetical target implies an **Enterprise Value
  of roughly $2.2bn (25th pctile) to $3.6bn (75th pctile)**, median ≈ $2.8bn — versus a
  meaningfully wider range off EV/Revenue, underscoring why multiple methodologies should be
  triangulated rather than relied on individually.
