# Comparable Company Analysis (Comps) — Theory

## What it is

Comparable company analysis ("trading comps") values a company by looking at how the
public market prices similar businesses, then applying those pricing ratios (multiples)
to the target's own financials. It answers: *"what would the market pay for this company
if it traded like its peers?"*

It is one of three core valuation methodologies used in banking, alongside a **DCF**
(intrinsic value from projected cash flows) and **precedent transactions** (what acquirers
have actually paid for similar companies, including a control premium). Comps are fast,
market-grounded, and the standard sanity check against a DCF.

## Step 1 — Select the peer group

Peers should be similar in:
- **Business model** (franchised vs. company-operated restaurants materially changes margins)
- **Sector/end market** (QSR vs. fast-casual vs. full-service)
- **Size** (a $3bn company and a $250bn company rarely deserve the same multiple)
- **Growth profile and geography**

Here the peer group is US-listed fast food / QSR names: MCD, YUM, QSR, WEN, SHAK, DPZ, CMG.
Note the mix is deliberately imperfect — MCD and CMG are far larger and higher-margin than
WEN or SHAK — to illustrate why multiple *dispersion* matters, not just the average.

## Step 2 — Calculate Enterprise Value (EV)

```
EV = Market Capitalization + Total Debt + Minority Interest + Preferred Equity − Cash & Equivalents
```

EV represents the value of the whole operating business, independent of how it's financed —
which is why EV is paired with *pre-interest* metrics like Revenue and EBITDA, while Price
and Net Income (equity-level metrics, after interest expense) are paired with each other.

## Step 3 — Compute trading multiples

| Multiple | Formula | Best used when |
|---|---|---|
| EV / Revenue | EV ÷ LTM Revenue | Company is unprofitable or margins vary wildly across peers |
| EV / EBITDA | EV ÷ LTM EBITDA | The standard cross-capital-structure multiple; most commonly quoted |
| EV / EBIT | EV ÷ LTM EBIT | Useful when D&A/capex intensity differs a lot between peers (e.g. franchised vs. owned real estate) |
| P / E | Price ÷ Diluted EPS | Simple and widely quoted, but distorted by capital structure (leverage) and non-operating items |

## Step 4 — Summarize the peer set

Don't just average the peers — report the **min, 25th percentile, median, 75th percentile,
and max**. The median is usually the primary anchor because it's less distorted by outliers
than the mean (see "pitfalls" below).

## Step 5 — Apply to the target

Multiply the target's own Revenue/EBITDA by the peer set's multiple range to get an
**implied EV range**, then back out **implied equity value**:

```
Implied EV = Peer Multiple × Target Metric
Implied Equity Value = Implied EV − Target Net Debt
```

Running this at the 25th percentile, median, and 75th percentile produces a *valuation
range*, not a single number — which is the standard output bankers present (often laid
out as a "football field" chart alongside DCF and precedent transaction ranges).

## Common pitfalls (and what this project demonstrates)

1. **Outliers skew the mean.** In the output data, Shake Shack's low LTM net income vs.
   its market cap produces a P/E of ~172x, dragging the peer-set mean P/E to ~49x while the
   median stays a much more sane ~29x. This is why median (or a trimmed range) is preferred
   over a simple average.
2. **Mixing business models.** MCD is ~90%+ franchised (asset-light, high margin);
   Wendy's and Shake Shack run more company-operated stores (lower margin, more capex).
   A single "fair" multiple doesn't really exist across that mix — it's a range for a reason.
3. **LTM vs. forward.** This model uses trailing (LTM) financials for simplicity. Desks
   more commonly use forward (NTM) estimates, which better reflect where the market is
   actually pricing growth.
4. **EV bridge completeness.** Operating leases, pension obligations, and non-controlling
   interests can materially change EV for some companies (this simplified model ignores
   leases — a real desk would not).
