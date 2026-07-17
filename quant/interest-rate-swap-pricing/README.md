# Interest Rate Swap Pricing

Builds a discount factor curve from zero rates, derives implied forward rates, prices a
fixed-for-floating swap's two legs via two independently cross-checked methods, solves for the
par swap rate, marks an existing off-market swap to market, and computes DV01 with an
explicitly-stated sign convention.

For the theory behind curve-based swap pricing and the DV01 sign convention, see
[`theory/swap_pricing_theory.md`](theory/swap_pricing_theory.md).

## What the code does

1. **Loads a zero-rate curve** ([`data/yield_curve.csv`](data/yield_curve.csv)) and **swap
   terms** ([`data/swap_terms.csv`](data/swap_terms.csv)) — notional, maturity, and an existing
   contractual fixed rate.
2. **Builds discount factors** from zero rates and **derives implied forward rates**.
3. **Prices the floating leg two independent ways** (a closed-form shortcut and a manual
   forward-rate summation) and verifies they agree to floating-point precision.
4. **Solves for the par swap rate** (zero NPV at inception) and verifies it directly.
5. **Marks the existing off-market swap to market**, computing NPV to the fixed-rate payer.
6. **Computes DV01** via a curve bump-and-reprice (±1bp), with an explicit, unambiguous sign
   convention stated in the output.
7. **Outputs**: curve detail CSV, a summary text file, a curve/forward-rate chart, and a
   leg-PV comparison chart.

## Data note

The yield curve and swap terms are **illustrative** — this environment couldn't reach live
market data (network/SSL restriction). The pricing mechanics are exactly what you'd run
against a real market discount curve.

## How to run

```bash
cd code
pip install -r requirements.txt
python swap_pricing_model.py
```

Outputs are written to `output/`.

## Folder structure

```
interest-rate-swap-pricing/
├── code/
│   ├── swap_pricing_model.py
│   └── requirements.txt
├── data/
│   ├── yield_curve.csv
│   └── swap_terms.csv
├── theory/
│   └── swap_pricing_theory.md
├── output/                  # generated curve detail, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Par Swap Rate: 4.1952%**, verified to produce ~$0 NPV when priced directly.
- **Floating leg PV cross-check**: shortcut and manual methods agree to within **7.11e-15** —
  strong verification the curve mechanics are correctly implemented.
- **Existing swap (3.80% contractual rate) has an NPV of +$1.75mm to the fixed-rate payer** —
  they're locked into paying below the current 4.1952% par rate, a real economic benefit.
- **DV01: +$0.0438mm per 1bp of parallel rate increase** — correctly signed and explained: the
  fixed payer gains as rates rise, since they keep paying a fixed rate while receiving an
  increasingly valuable floating leg.
