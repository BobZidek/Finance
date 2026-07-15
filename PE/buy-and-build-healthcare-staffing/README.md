# Buy-and-Build (Add-On Acquisition) Model — Healthcare Staffing

Models a platform acquisition ("Summit Health Staffing") followed by 3 bolt-on acquisitions
at staggered years during a 5-year hold, bought at lower multiples than the platform's own
exit multiple — the "multiple arbitrage" thesis at the core of every roll-up strategy.

For the theory behind multiple arbitrage and the modeling approach, see
[`theory/buy_and_build_strategy.md`](theory/buy_and_build_strategy.md).

## What the code does

1. **Loads platform and deal assumptions** ([`data/platform_and_deal_assumptions.csv`](data/platform_and_deal_assumptions.csv))
   and **bolt-on acquisitions** ([`data/bolt_on_acquisitions.csv`](data/bolt_on_acquisitions.csv))
   — each bolt-on's acquisition year, EBITDA at acquisition, purchase multiple, debt turns,
   and synergy run-rate.
2. **Builds combined EBITDA year by year**: each entity (platform + acquired-to-date bolt-ons)
   grows organically from its own acquisition date, plus a 2-year integration synergy ramp
   (0% / 50% / 100%) once acquired.
3. **Builds a combined debt schedule**: tracks a single running debt balance across multiple
   draws (one at each acquisition), swept down each year using the combined entity's growing
   free cash flow capacity.
4. **Tracks sponsor equity contributed at each of the 4 acquisition dates** (platform + 3
   bolt-ons), not just a single entry check.
5. **Computes exit value and sponsor returns**: exit EV at the platform's exit multiple ×
   combined exit EBITDA, minus remaining debt, minus total equity invested (MOIC), with a
   **true multi-date IRR** via bisection search (reusing the fund model's IRR solver).
6. **Outputs**: a summary text file, the full year-by-year build-up schedule CSV, an EBITDA
   build-up chart (stacked by entity), and a debt-vs-equity-by-year chart.

## Data note

The platform and all 3 bolt-ons are **fictional/illustrative** — a mechanics demonstration
of buy-and-build modeling rather than an analysis of a real roll-up. The engine (multi-date
equity contributions, combined debt schedule across staggered draws, synergy ramp) mirrors a
real buy-and-build model exactly.

## How to run

```bash
cd code
pip install -r requirements.txt
python buy_and_build_model.py
```

Outputs are written to `output/`.

## Folder structure

```
buy-and-build-healthcare-staffing/
├── code/
│   ├── buy_and_build_model.py
│   └── requirements.txt
├── data/
│   ├── platform_and_deal_assumptions.csv
│   └── bolt_on_acquisitions.csv
├── theory/
│   └── buy_and_build_strategy.md
├── output/                  # generated summary, build-up schedule, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Weighted-average entry multiple across all 4 acquisitions: 7.18x**, against a **9.5x exit
  multiple** — a **+2.32x multiple arbitrage spread**.
- **Combined EBITDA grows from $30mm (platform alone) to $71.1mm** by exit — through organic
  growth on all four entities plus fully-ramped integration synergies on the three bolt-ons.
- **Total sponsor equity invested across all four acquisition dates: $205.4mm** (not a single
  entry check — capital was contributed at Years 0, 1, 2, and 3).
- The deal returns **2.75x MOIC / 27.1% IRR** — meaningfully higher than what the platform's
  own standalone growth would have produced, illustrating why multiple arbitrage is the
  central value driver in a buy-and-build strategy, not just an incidental benefit.
