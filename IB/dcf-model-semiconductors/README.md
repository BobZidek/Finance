# DCF Model — Semiconductors (Texas Instruments)

A 5-year unlevered free cash flow DCF for Texas Instruments (TXN), with WACC derived via
CAPM, a Gordon Growth terminal value, and a WACC × terminal-growth sensitivity table.

For the theory behind each step, see [`theory/dcf_valuation.md`](theory/dcf_valuation.md).

## What the code does

1. **Loads assumptions** from [`data/dcf_assumptions.csv`](data/dcf_assumptions.csv) (CAPM
   inputs, capital structure weights, tax rate, terminal growth, shares outstanding, net debt)
   and year-by-year forecast drivers from [`data/forecast_drivers.csv`](data/forecast_drivers.csv)
   (revenue growth, EBIT margin, D&A%, capex%, ΔNWC% by year).
2. **Computes WACC** via CAPM for cost of equity, blended with after-tax cost of debt.
3. **Builds the 5-year UFCF forecast**: Revenue → EBIT → NOPAT → + D&A − Capex − ΔNWC.
4. **Discounts each year's FCF** at WACC and computes a Gordon Growth terminal value,
   discounted back to present value.
5. **Backs into implied Enterprise Value → Equity Value → Share Price.**
6. **Builds a sensitivity table**: implied share price across a WACC × terminal-growth grid
   (±1% around the base case in 0.5% steps).
7. **Outputs**: forecast CSV, sensitivity table CSV, a text summary, an FCF forecast chart,
   and a sensitivity heatmap.

## Data note

Assumptions (margins, growth rates, capital structure, beta) are **illustrative,
hand-set inputs** — this environment couldn't reach live market/financial data APIs
(network/SSL restriction), so real TXN figures were approximated from general knowledge
rather than pulled live. **The implied share price should not be read as an actual
market call on TXN** — it demonstrates the mechanics and sensitivity of the DCF method,
not a live investment thesis. Swap in real 10-K figures and analyst consensus estimates
to make this an actual valuation (see [`ENHANCEMENTS.md`](ENHANCEMENTS.md)).

## How to run

```bash
cd code
pip install -r requirements.txt
python dcf_model.py
```

Outputs are written to `output/`.

## Folder structure

```
dcf-model-semiconductors/
├── code/
│   ├── dcf_model.py          # main analysis script
│   └── requirements.txt
├── data/
│   ├── dcf_assumptions.csv   # CAPM inputs, capital structure, tax, terminal growth
│   └── forecast_drivers.csv  # year-by-year revenue growth / margin / capex assumptions
├── theory/
│   └── dcf_valuation.md
├── output/                   # generated forecast, sensitivity table, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **WACC ≈ 9.68%**, built from a cost of equity of ~10.35% (CAPM) and after-tax cost of debt
  of ~3.6%, weighted 90/10 equity/debt.
- **Enterprise Value ≈ $70.2bn**, Equity Value ≈ $62.3bn, implying a **share price of ~$68.44**
  under the base-case assumptions.
- **~75% of Enterprise Value comes from the terminal value**, not the 5-year explicit forecast —
  the central structural weakness of any DCF, and worth calling out explicitly rather than
  glossing over (see the theory doc's critique section).
- The sensitivity table shows implied share price ranging from **~$53 to ~$96** across a
  ±1% WACC / ±1% terminal growth grid — a reminder that a DCF output is a range, not a point
  estimate.
