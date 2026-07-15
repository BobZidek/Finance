# SaaS Metrics Dashboard — Fieldwork

Computes the core SaaS unit-economics and efficiency metrics — CAC, LTV, LTV:CAC, gross/net
revenue retention, CAC payback, burn multiple, and the SaaS magic number — from 8 quarters of
data for a hypothetical B2B field service management SaaS startup ("Fieldwork"), and charts
how each evolves as the company scales.

For the theory behind each metric and how to interpret them, see
[`theory/saas_metrics_theory.md`](theory/saas_metrics_theory.md).

## What the code does

1. **Loads 8 quarters of raw data** ([`data/quarterly_metrics.csv`](data/quarterly_metrics.csv))
   — starting ARR, new/expansion/churned ARR, customer counts, S&M spend, gross margin, net burn.
2. **Computes retention**: Gross Revenue Retention and Net Revenue Retention per quarter.
3. **Computes unit economics**: CAC, LTV (via ARPA × gross margin ÷ churn rate), LTV:CAC ratio,
   and CAC payback period in months.
4. **Computes efficiency metrics**: Burn Multiple (net burn ÷ net new ARR) and the SaaS Magic
   Number (annualized QoQ ARR growth ÷ prior quarter's S&M spend).
5. **Outputs**: the full metrics dashboard CSV, a summary text file, an ARR growth chart, a
   GRR/NRR retention chart, and a combined LTV:CAC / Burn Multiple efficiency chart.

## Data note

The company and all financials are **fictional/illustrative** — a mechanics demonstration
of SaaS metrics calculation, deliberately designed to show metrics *improving* over time
(rather than uniformly excellent from day one) since that's the realistic, credible pattern
VCs actually look for.

## How to run

```bash
cd code
pip install -r requirements.txt
python saas_metrics_model.py
```

Outputs are written to `output/`.

## Folder structure

```
saas-metrics-dashboard/
├── code/
│   ├── saas_metrics_model.py
│   └── requirements.txt
├── data/
│   └── quarterly_metrics.csv
├── theory/
│   └── saas_metrics_theory.md
├── output/                  # generated dashboard, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included data snapshot)

- **ARR grows from $800K (Q1 start) to $4.75M (Q8 end)** — nearly 5x over 2 years.
- **NRR crosses 100% in Q4 and reaches 103.7% by Q8** — the company is now growing even
  without new logos, from expansion revenue alone exceeding churn.
- **LTV:CAC improves from a concerning 1.3x in Q1 to a healthy 3.2x by Q8** — unit economics
  going from unproven to solid as retention and ARPA improve.
- **Burn Multiple improves from 2.70x to 0.88x**, crossing below the 1.0x "great" threshold.
- **The Magic Number (~2.5-3.2x) reads as very high** — but the theory doc explains why that's
  a function of this company's unusually fast growth rate, not something to take at textbook
  face value without adjusting for growth pace.
