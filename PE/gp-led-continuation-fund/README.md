# GP-Led Continuation Fund Transaction — Crestpoint Industrial Services

Models a single-asset GP-led secondary transaction — a very current PE structure — where an
aging fund's sole remaining portfolio company moves into a new continuation vehicle at a
negotiated NAV, existing LPs choose to roll or cash out, and the GP crystallizes carry on the
old fund's gain immediately, then can earn carry again on the new fund's subsequent gain at
the eventual exit. This project **precisely quantifies the real "double-dip" carry critique**
of continuation fund structures.

For the theory behind continuation funds and the conflict of interest at their center, see
[`theory/continuation_fund_theory.md`](theory/continuation_fund_theory.md).

## What the code does

1. **Loads transaction assumptions** ([`data/transaction_assumptions.csv`](data/transaction_assumptions.csv))
   — old fund cost basis, transaction NAV, rolling LP %, carry %, and the future exit assumption.
2. **Models the continuation transaction**: computes old fund gain and GP carry crystallized,
   splits net LP proceeds between rolling LPs (reinvested) and cash-out LPs (paid by new
   secondary investors buying in at the same NAV basis).
3. **Models the continuation fund's eventual exit**: computes the new fund's gain (against its
   fresh, post-transaction cost basis), a second GP carry crystallization, and MOIC/IRR for
   both rolling LPs and new secondary investors.
4. **Compares total two-step carry against what a single continuous fund would have earned**
   on the identical original-cost-basis-to-final-exit outcome — quantifying the "double-dip" precisely.
5. **Outputs**: a summary text file, a carry comparison chart, and an investor outcomes chart.

## Data note

The company and all transaction terms are **fictional/illustrative** — a mechanics
demonstration of GP-led continuation fund structuring rather than an analysis of a real
transaction.

## How to run

```bash
cd code
pip install -r requirements.txt
python continuation_fund_model.py
```

Outputs are written to `output/`.

## Folder structure

```
gp-led-continuation-fund/
├── code/
│   ├── continuation_fund_model.py
│   └── requirements.txt
├── data/
│   └── transaction_assumptions.csv
├── theory/
│   └── continuation_fund_theory.md
├── output/                  # generated summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Structure | Total GP Carry |
|---|---|
| Two-step (continuation + eventual exit) | **$119.2mm** |
| Single continuous fund (same final outcome) | $106.0mm |
| **Difference** | **+$13.2mm (+12.5%)** |

- **The continuation structure produces 12.5% more total GP carry** than a single continuous
  fund would have earned on the identical final outcome — purely a mechanical consequence of
  crystallizing carry twice on overlapping value creation.
- **Rolling LPs and new secondary investors both earn the same 1.554x MOIC / 11.7% IRR** from
  the transaction to the eventual exit — exactly what a fairly-priced transaction should
  produce, since both invest at the same $/NAV basis.
- This is the precise, quantified version of the real "double-dip" critique of GP-led
  continuation funds, and exactly why independent fairness opinions and LP Advisory Committee
  sign-off are standard governance features of these transactions.
