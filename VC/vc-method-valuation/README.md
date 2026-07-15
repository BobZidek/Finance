# VC Method Valuation — NovaCart

Values a hypothetical early-stage SMB e-commerce checkout/payments startup ("NovaCart") using
the VC Method — working backward from an assumed exit value and required return multiple to
an implied valuation today — computing both the naive version and the version correctly
adjusted for dilution from anticipated future financing rounds.

For the theory behind the method and why the dilution adjustment matters, see
[`theory/vc_method_theory.md`](theory/vc_method_theory.md).

## What the code does

1. **Loads valuation assumptions** ([`data/valuation_assumptions.csv`](data/valuation_assumptions.csv))
   — assumed exit value, required ROI, investment amount, years to exit.
2. **Loads anticipated future financing rounds** ([`data/future_dilution_rounds.csv`](data/future_dilution_rounds.csv))
   — the expected dilution % from each round between now and exit.
3. **Computes the retention ratio** — the product of (1 − dilution%) across all anticipated
   future rounds.
4. **Computes both the naive VC Method** (ignoring future dilution) **and the correctly
   adjusted version** (dividing target exit ownership by the retention ratio), showing the
   valuation gap between them.
5. **Builds a sensitivity table**: dilution-adjusted pre-money valuation across a 5×5 Exit
   Value × Required ROI grid.
6. **Outputs**: a valuation summary text file, sensitivity table CSV, a naive-vs-adjusted
   comparison chart, and a sensitivity heatmap.

## Data note

The startup and all financial assumptions are **fictional/illustrative** — a mechanics
demonstration of the VC Method rather than an actual valuation of a real company.

## How to run

```bash
cd code
pip install -r requirements.txt
python vc_method_model.py
```

Outputs are written to `output/`.

## Folder structure

```
vc-method-valuation/
├── code/
│   ├── vc_method_model.py
│   └── requirements.txt
├── data/
│   ├── valuation_assumptions.csv
│   └── future_dilution_rounds.csv
├── theory/
│   └── vc_method_theory.md
├── output/                  # generated summary, sensitivity table, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- At a **$500mm assumed exit value, 15x required ROI, and $5mm investment**, the **naive VC
  Method implies a $28.33mm pre-money valuation** — but correctly adjusting for two
  anticipated future rounds (Series B at 20% dilution, Series C at 15%) drops that to
  **$17.67mm**, a **~60% overstatement** from ignoring dilution.
- The **retention ratio is 68.0%** — only 68% of today's ownership stake is expected to
  survive to exit after two more financing rounds.
- The sensitivity table shows dilution-adjusted pre-money valuation ranging from **$1.8mm**
  (30x ROI target / $300mm exit) to **$46.0mm** (10x ROI target / $750mm exit) — a >25x spread
  across plausible assumption combinations, underscoring how much the *inputs* — not the
  formula — drive the outcome of a VC Method valuation.
