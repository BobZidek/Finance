# Portfolio Company Debt Refinancing — Theory

## How this differs from a dividend recap

[`IB/dividend-recap-credit-analysis`](../../IB/dividend-recap-credit-analysis) modeled raising
**additional** debt to fund a special dividend — increasing leverage to extract cash for the
sponsor. **This project models something different**: refinancing the **same** amount of
existing debt at better terms (lower rate, longer maturity), with **no** dividend extraction
and **no change in leverage**. It's a pure cost-of-capital optimization exercise — the kind of
opportunistic transaction a portfolio company's CFO and sponsor pursue purely to reduce ongoing
interest expense and push out maturity risk, unrelated to returning capital to the sponsor.

## Why a company would have this opportunity

A portfolio company's achievable borrowing rate typically improves over a hold period for two
independent reasons: (1) **the company itself de-risks** — EBITDA growth and debt paydown
since the original financing reduce leverage and improve coverage ratios, making the same
company a better credit than it was at LBO close; and (2) **credit markets move** — spreads
tighten or benchmark rates fall independent of anything company-specific. This project's
150bp rate improvement (9.25% -> 7.75%) plausibly reflects both effects combined.

## The core NPV framework

```
Annual Interest Savings = Outstanding Principal x (Existing Rate − New Rate)
Cash Refinancing Costs = New OID + New Arrangement/Legal Fees
NPV of Interest Savings = PV of an annuity of Annual Savings over the remaining term
                            (discounted at the new rate)
NPV of Refinancing = NPV of Interest Savings − Cash Refinancing Costs
```

This project's base case: **$6.0mm of annual interest savings** on $400mm of principal,
against **$3.5mm of upfront cash costs** (OID + arrangement fees) — producing a strongly
**positive $16.5mm NPV** over the existing debt's 4-year remaining term.

## Why the discount horizon matters: using the conservative comparison window

The NPV calculation here uses the **existing debt's remaining maturity (4 years)** as the
comparison window, even though the new debt is priced with a **5-year** term. This is the
conservative, defensible choice: the fifth year of savings is only "extra" value if you assume
the company would otherwise have needed to refinance again in year 4 anyway — comparing
"apples to apples" over the period both instruments would have covered avoids overstating the
refinancing's benefit with an extra year of savings that isn't a genuine like-for-like comparison.

## The breakeven period — a fast, intuitive sanity check

```
Breakeven (Payback) Period = Cash Refinancing Costs / Annual Savings
```

This project's breakeven is just **0.58 years (~7 months)** — the refinancing costs pay for
themselves in interest savings well within the first year, after which every remaining year of
the loan's term is pure savings. A short payback period like this is a strong, easy-to-explain
signal (alongside the more rigorous NPV) that a refinancing is economically attractive, and
it's often the number a company's board or credit committee anchors on first, precisely because
it doesn't require agreeing on a discount rate the way NPV does.

## The breakeven rate — how much execution risk is there?

```
Breakeven New Rate = the achievable new rate at which NPV of Refinancing = 0
```

The actual rate a company can achieve in the market isn't known with certainty until the deal
is actually marketed to lenders — this project's **8.98% breakeven rate** means the company
has **27 basis points of cushion** below its existing 9.25% rate: even if market execution
comes in worse than the targeted 7.75%, the refinancing remains NPV-positive all the way up to
8.98%. A wide cushion like this indicates low execution risk; a breakeven rate very close to
the existing rate would signal a refinancing that only makes sense if pricing comes in almost
exactly as hoped — a meaningfully riskier proposition to bring to a credit committee.

## The unamortized fee write-off — a real cost, but not a cash one

This project's summary notes **$1.8mm of unamortized fees on the old debt** that would be
written off (expensed) upon refinancing — a real GAAP charge that reduces reported earnings in
the period of the refinancing, but **not a new cash outflow**, since those fees were paid
years ago when the original debt was issued. Distinguishing cash costs (which belong in the
NPV analysis) from non-cash accounting charges (which affect reported earnings but not the
economic decision) is a standard and important discipline in any refinancing analysis.
