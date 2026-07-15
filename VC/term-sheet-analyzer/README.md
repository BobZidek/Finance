# Term Sheet Analyzer — Liquidation Preferences (Brightline Robotics)

Compares three liquidation preference structures for a hypothetical Series B investment
("Brightline Robotics") across a range of exit values: **1x non-participating preferred**,
**1x participating preferred (uncapped)**, and **1x participating preferred with a 3x cap** —
showing exactly how much each pays the investor (and what's left for common/founders) at
every exit value, and identifying the crossover points where each structure's behavior changes.

For the theory behind each structure and how to read the crossover points, see
[`theory/liquidation_preferences.md`](theory/liquidation_preferences.md).

## What the code does

1. **Loads term sheet assumptions** ([`data/term_sheet_assumptions.csv`](data/term_sheet_assumptions.csv))
   — Series B investment amount, as-converted ownership %, preference multiple, and
   participation cap multiple.
2. **Computes payouts across 11 exit value scenarios** ($10mm to $350mm) for all three
   structures:
   - **Non-participating**: `max(preference, as-converted)`
   - **Participating (uncapped)**: `preference + pro-rata share of the remainder`
   - **Participating (capped)**: the uncapped participating amount, capped at a multiple of
     invested capital, but never less than straight as-converted
3. **Identifies the two key crossover exit values**: where non-participating converts to
   common, and where the participation cap starts binding.
4. **Outputs**: a full comparison CSV, a term sheet summary text file with the crossover
   values called out explicitly, a payout-by-structure chart, and a common/founder-impact chart.

## Data note

The startup and all deal terms are **fictional/illustrative** — a mechanics demonstration of
liquidation preference structures rather than an analysis of a real term sheet.

## How to run

```bash
cd code
pip install -r requirements.txt
python term_sheet_model.py
```

Outputs are written to `output/`.

## Folder structure

```
term-sheet-analyzer/
├── code/
│   ├── term_sheet_model.py
│   └── requirements.txt
├── data/
│   └── term_sheet_assumptions.csv
├── theory/
│   └── liquidation_preferences.md
├── output/                  # generated comparison, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Non-participating preferred converts to common at a $75mm exit value** — exactly where
  the investor's 20% as-converted share equals their $15mm preference.
- **Participating (uncapped) always pays at least as much as non-participating**, with the
  gap growing as exit value rises — e.g. **$42mm vs. $30mm at a $150mm exit**, a $12mm
  transfer from common/founders to the investor purely from the participation term.
- **The 3x cap ($45mm) binds above a ~$200mm exit value**, and the capped structure
  eventually **converges back to non-participating economics at very high exit values**
  ($70mm for both at a $350mm exit) — since the investor is guaranteed at least what straight
  conversion would pay.
- At modest exits, all three structures produce similar payouts; the differences only become
  material at larger exits — exactly where founders have the most to lose from conceding
  participation rights.
