# Full Investment Memo — Vertex Retrieval (Series A)

The VC capstone project: Series A deal terms, dilution-adjusted ownership, and Bear/Base/Bull
exit scenario returns for a hypothetical vector database / RAG infrastructure startup
("Vertex Retrieval"), packaged with the market analysis, risk factors, and team assessment
sections of a real VC investment memo — explicitly tying together the market sizing, cap
table dilution, and VC method concepts from the other VC projects in this repo.

**The actual memo is in [`theory/investment_memo_narrative.md`](theory/investment_memo_narrative.md)**
— read that for the full memo (executive summary, market analysis, team assessment, risk
factors, quantitative summary, recommendation). This README covers the quantitative engine
behind it.

## What the code does

1. **Loads deal assumptions** ([`data/deal_assumptions.csv`](data/deal_assumptions.csv)) —
   current ARR/customers/NRR/burn multiple, proposed Series A terms, years to exit, and an
   assumed future-dilution retention ratio (same concept as
   [`VC/vc-method-valuation`](../vc-method-valuation)).
2. **Loads 3 exit scenarios** ([`data/exit_scenarios.csv`](data/exit_scenarios.csv)) — Bear,
   Base, and Bull exit values, with the Bull case calibrated to be consistent with the SOM
   sized in [`VC/market-sizing-ai-infra`](../market-sizing-ai-infra).
3. **Computes deal terms**: post-money valuation, ownership at close, implied ARR multiple,
   and **effective ownership at exit** after applying the future-dilution retention ratio.
4. **Computes MOIC and IRR for each exit scenario**, using the investor's dilution-adjusted
   effective ownership.
5. **Outputs**: a quantitative summary text file, scenario returns CSV, a scenario returns
   chart (MOIC bars + IRR line), and an ownership dilution bridge chart.

## Data note

The startup and all deal terms are **fictional/illustrative** — a mechanics demonstration
tying together concepts from across the VC project set, not an actual investment analysis.
The market category (vector databases / AI retrieval infrastructure) references general,
well-known market dynamics, not claims about any specific real company.

## How to run

```bash
cd code
pip install -r requirements.txt
python investment_memo_model.py
```

Outputs are written to `output/`.

## Folder structure

```
investment-memo-startup/
├── code/
│   ├── investment_memo_model.py
│   └── requirements.txt
├── data/
│   ├── deal_assumptions.csv
│   └── exit_scenarios.csv
├── theory/
│   └── investment_memo_narrative.md   <- the actual investment memo
├── output/                  # generated summary, scenario returns, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Scenario | Exit Value | Investor Payout | MOIC | IRR |
|---|---|---|---|---|
| Bear | $80mm | $10.4mm | 0.87x | -2.4% |
| Base | $400mm | $52.0mm | 4.33x | 27.7% |
| Bull | $1,500mm | $195.0mm | 16.25x | 59.2% |

- Series A: **$12mm at $60mm post-money (25.0x current ARR)** — a rich multiple reflecting
  strong category momentum.
- **Ownership at close (20.0%) falls to an effective 13.0% at exit** after accounting for two
  anticipated future rounds of dilution — the same mechanics as
  [`VC/vc-method-valuation`](../vc-method-valuation), applied here to an actual deal decision.
- The **Bear case is a modest loss (0.87x)** — a realistic downside, not a worst-case wipeout,
  consistent with this being a Series A investment in a company with real revenue and traction
  rather than a pure seed-stage bet.
- See the full narrative memo for the market, team, and risk sections that turn this
  quantitative output into an actual investment recommendation.
