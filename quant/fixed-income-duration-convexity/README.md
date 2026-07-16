# Fixed Income Duration, Convexity & Key Rate Duration

Prices a 4-bond portfolio off a hand-specified, linearly-interpolated yield curve, computes
duration and convexity for each bond, validates the duration+convexity price approximation
against actual re-pricing at yield shocks up to ±300bps, and computes Key Rate Durations —
portfolio sensitivity to individual points on the yield curve.

For the theory behind duration, convexity, and Key Rate Duration, see
[`theory/duration_convexity_theory.md`](theory/duration_convexity_theory.md).

## What the code does

1. **Loads a yield curve** ([`data/yield_curve.csv`](data/yield_curve.csv)) — spot rates at
   2, 5, 10, and 30 years — and a **4-bond portfolio** ([`data/bond_portfolio.csv`](data/bond_portfolio.csv))
   with maturities (3, 7, 12, 20 years) deliberately falling **between** the curve's key points.
2. **Prices each bond** using its yield linearly interpolated from the curve, and computes
   **Macaulay duration, modified duration, and convexity** via standard discrete cash-flow formulas.
3. **Validates the duration+convexity price approximation** against actual re-pricing at yield
   shocks from -300bps to +300bps on the longest-duration bond, quantifying exactly how much
   convexity improves the approximation.
4. **Computes Key Rate Durations**: bumps each curve point individually by 1bp and re-prices
   every bond, splitting each bond's total sensitivity across the bracketing key maturities
   proportional to interpolation weight — and verifies KRDs sum to each bond's modified duration.
5. **Outputs**: bond analysis CSV, price shock validation CSV, Key Rate Duration CSV, a
   price-shock-accuracy chart, and a stacked KRD-by-bond chart.

## Data note

The yield curve and bond portfolio are **illustrative** — this environment couldn't reach live
market data (network/SSL restriction). The bond pricing, duration, convexity, and KRD
mechanics are exactly what you'd run against real market yield curve data.

## How to run

```bash
cd code
pip install -r requirements.txt
python fixed_income_model.py
```

Outputs are written to `output/`.

## Folder structure

```
fixed-income-duration-convexity/
├── code/
│   ├── fixed_income_model.py
│   └── requirements.txt
├── data/
│   ├── yield_curve.csv
│   └── bond_portfolio.csv
├── theory/
│   └── duration_convexity_theory.md
├── output/                  # generated bond analysis, shock validation, KRD, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Portfolio Modified Duration: 7.93, Portfolio Convexity: 97.97.**
- **Convexity dramatically improves the price approximation for large yield moves**: at a
  -300bp shock on the longest bond, duration-only estimates the price change at +39.7% (a
  -12.6 percentage point error vs. the actual +52.3%); adding convexity brings the estimate to
  +50.0% (error shrinks to just -2.3 percentage points) — roughly a **5.5x reduction in
  approximation error**.
- **Key Rate Durations correctly split each bond's sensitivity across the bracketing curve
  points** — e.g., the 20-year bond (exactly midway between the 10-year and 30-year key rates)
  shows an almost perfectly even 6.61/6.61 split.
- **Each bond's KRDs sum almost exactly to its overall Modified Duration** — a built-in
  mathematical consistency check confirming the KRD calculation is correct.
