# Potential Enhancements

- **Cohort-based retention**: replace the aggregate quarterly GRR/NRR with true cohort
  retention curves (tracking each signup cohort's revenue over subsequent quarters), which is
  more precise and reveals whether retention is improving for new cohorts specifically or just
  averaging up because of an improving mix.
- **Segment breakdown**: split metrics by customer segment (SMB vs. mid-market vs. enterprise),
  since blended CAC/LTV often hides very different unit economics across segments.
- **Growth-rate-normalized Magic Number benchmark**: build the adjustment the theory doc
  describes explicitly — a formula or lookup table that adjusts the "good" Magic Number
  threshold based on the company's actual YoY growth rate, rather than a single fixed 0.75/1.0
  benchmark.
- **Rule of 40 cross-check**: add the Rule of 40 score (growth % + FCF margin %) from
  [`IB/comps-dashboard-saas`](../../IB/comps-dashboard-saas) as a complementary efficiency lens.
- **Sales channel mix**: split CAC and Magic Number by acquisition channel (outbound sales,
  inbound/PLG, partnerships) to identify which channel is actually driving efficient growth.
- **Forward projection**: extend the 8 quarters of historical data into a forward-looking
  projection, using the trend in each metric to forecast when the company might reach specific
  efficiency milestones (e.g., burn multiple consistently below 1.0x).
- **Live data pipeline**: connect to a real billing/CRM data source (Stripe, Salesforce) to
  compute these metrics automatically from actual transaction data instead of a static CSV.
