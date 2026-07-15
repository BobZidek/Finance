# SaaS Metrics — Theory

## Why these specific metrics

VC due diligence on a SaaS company centers on one question: **is growth actually creating
durable value, or just burning cash to look big?** No single metric answers that — each one
this project computes captures a different failure mode a fast-growing SaaS company can hide
behind pure top-line growth.

## Revenue retention: GRR vs. NRR

```
GRR (Gross Revenue Retention) = (Starting ARR − Churned ARR) / Starting ARR
NRR (Net Revenue Retention)   = (Starting ARR − Churned ARR + Expansion ARR) / Starting ARR
```

**GRR can never exceed 100%** — it measures pure retention, ignoring any upsell. **NRR can
exceed 100%** when expansion revenue from existing customers (upsells, seat growth) outpaces
churn — a company with NRR > 100% is growing even if it never signs another new customer,
which is why NRR above ~110-120% is one of the single strongest signals of product quality
and stickiness a SaaS company can show. In this project's data, **NRR crosses 100% in Q4 and
reaches 103.7% by Q8** — a healthy trajectory, though not yet in the "best-in-class" 115%+
range some top SaaS companies achieve.

## CAC, LTV, and the LTV:CAC ratio

```
CAC = Sales & Marketing Spend / New Customers Acquired
LTV = (Quarterly ARPA x Gross Margin %) / Quarterly Customer Churn Rate
LTV:CAC = LTV / CAC
```

LTV approximates the total gross profit a customer generates over their expected lifetime
(1/churn rate = expected lifetime in quarters). **LTV:CAC of 3x+ is the standard "healthy"
benchmark** — below that, a company is spending too much to acquire customers relative to
what they're worth; well above ~5-6x can actually signal the company is *underinvesting* in
growth relative to its opportunity. This project's LTV:CAC starts at a **concerning 1.3x in
Q1** and climbs to a **healthy 3.2x by Q8** — exactly the trajectory an investor wants to see:
not "always great," but *proving out* unit economics as the company matures and its retention
improves.

## CAC Payback Period

```
CAC Payback (months) = CAC / (Monthly ARPA x Gross Margin %)
```

How many months of gross profit from a customer it takes to recover their acquisition cost.
Under ~12 months is considered excellent for SaaS; 12-18 months is reasonable; beyond that,
capital gets tied up for a long time before each customer becomes profitable. This project's
payback **improves from ~31 months to ~24.5 months** — still on the longer side by Q8, a
realistic flag that would show up in real diligence even alongside improving LTV:CAC (the two
metrics don't always move in lockstep, since payback is driven by *near-term* gross profit
per customer while LTV also credits the *full* expected lifetime).

## Burn Multiple

```
Burn Multiple = Net Burn / Net New ARR   (same quarter)
```

Popularized by Bessemer Venture Partners: how many dollars of cash a company burns to
generate one dollar of *net new* annual recurring revenue. **Below 1x is considered great,
1-1.5x good, above 2x concerning** (for growth-stage companies specifically — early seed-stage
companies often run higher burn multiples while proving the product). This project's burn
multiple **improves from 2.70x in Q1 to 0.88x by Q8** — crossing below the 1.0x "great"
threshold, a strong capital-efficiency signal on top of the retention and LTV:CAC improvement.

## The SaaS Magic Number — and why this project's number runs high

```
Magic Number = (This Quarter's ARR − Prior Quarter's ARR) x 4 / Prior Quarter's S&M Spend
```

The textbook benchmark (>0.75 good, >1.0 very good) is **calibrated to companies growing at a
moderate, sustainable pace** (roughly 40-70% YoY). This project's company is growing far
faster than that (ARR nearly 5x's over 2 years, well over 100% annualized) — and **that
changes what a "normal" Magic Number looks like**. The formula annualizes a single quarter's
ARR growth (×4) against only the *prior* quarter's spend; for a company growing this fast,
each quarter's dollar growth is already large relative to the ARR base, which mechanically
pushes the ratio up even when S&M spend itself is a very large fraction of ARR (here,
$470K-$1.1M in quarterly S&M against an ARR base growing from $800K to $4.75M — a genuinely
heavy spend level, not a cheap one). **This project's Magic Number of ~2.5-3.2x should be read
as "very high, driven by an unusually fast growth rate" rather than simply "efficient" — the
metric needs to be interpreted alongside the company's actual growth rate, not against a
one-size-fits-all textbook threshold.** This nuance — that "great" benchmarks are themselves
growth-rate-dependent — is a genuinely important, often-missed point in SaaS metrics analysis.
