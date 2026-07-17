# Bank Valuation: P/TBV & ROE — Theory

## Why banks aren't valued like industrial companies

Every other valuation project in this repo centers on **Enterprise Value** — the value of the
operating business independent of financing, paired with EBITDA. That framework **doesn't work
for banks**: a bank's deposits and borrowings aren't optional financing choices layered on top
of an operating business — they're the **raw material of the business itself** (a bank
literally is in the business of borrowing cheap and lending dear). There's no clean way to
separate "operations" from "capital structure" for a bank, so EV/EBITDA is essentially never
used. Banks are instead valued on **Price/Tangible Book Value (P/TBV)**, anchored to
**Return on Equity (ROE)** relative to the **Cost of Equity**.

## The Justified P/TBV formula

```
Justified P/TBV = (ROE − g) / (Cost of Equity − g)
```

This is a Gordon Growth Model variant applied to book value instead of dividends directly — a
bank earning exactly its cost of equity should trade at **1.0x tangible book** (it creates no
excess economic value above what shareholders require); a bank earning **more** than its cost
of equity justifies trading **above** book (each dollar of equity compounds faster than
investors require); a bank earning **less** justifies trading **below** book. This project's
base case — 12.0% ROE against a 9.98% cost of equity — justifies **1.29x TBV**, meaningfully
above the 1.0x "no value creation" benchmark.

## The refinement most simplified bank valuations miss: excess capital

A bank's **required regulatory capital** is a function of its risk-weighted assets (RWA), not
its total book equity — `Required Capital = CET1 Ratio Requirement x RWA`. Any book equity
**above** that requirement is "excess capital" — capital the bank is holding but that isn't
actually needed to support its current balance sheet, and critically, **isn't earning the
bank's true operating ROE**, because it's typically parked in low-yielding, low-risk assets
(e.g. sitting in cash or short-term securities) rather than being deployed into the bank's core
lending business.

**Applying a single blended ROE to total book value understates true value**, because it drags
the bank's genuine operating profitability down by mixing in this non-compounding excess
capital. This project's fix: split book value into **core** (the required regulatory capital,
generating the bank's *true* core ROE) and **excess** (valued near book, since it isn't
compounding at the core rate), then value each separately:

```
Core ROE = Net Income / Required Capital           (higher than blended ROE, since the
                                                      denominator excludes non-earning excess capital)
Core Equity Value = Core Justified P/TBV x Required Capital
Excess Capital Value = Excess Capital x 1.0          (valued at book - it isn't compounding)
Sum-of-Parts Equity Value = Core Equity Value + Excess Capital Value
```

## Reading this project's results — the sum-of-parts value is materially higher

| Approach | Implied ROE | Justified P/TBV | Implied Equity Value |
|---|---|---|---|
| Blended (simple) | 12.00% | 1.29x | $1,096.8mm |
| **Sum-of-Parts (core + excess)** | 14.17% (core) | 1.60x (core) | **$1,282.7mm (1.51x blended)** |

The sum-of-parts approach implies an equity value **~17% higher** than the naive blended
approach — because the bank's *core* banking operations are genuinely more profitable (14.17%
ROE) than the blended 12.0% figure suggests, once the drag from $130mm of non-earning excess
capital is properly isolated rather than averaged in. This is a real, commonly-used technique
among bank equity analysts — a bank sitting on excess capital (from strong earnings retention,
a recent capital raise, or shrinking risk-weighted assets) is frequently **undervalued by
investors who only look at the blended ROE/P-TBV relationship**, and this decomposition is
exactly how that mispricing gets identified and argued.

## Why this project's bank trades below both justified values

The bank's **current market value ($892.5mm, 1.05x TBV)** sits below both the blended-ROE
justified value ($1,096.8mm, 1.29x) and — even more so — the sum-of-parts value ($1,282.7mm,
1.51x). A real analyst would treat this gap as the starting point for an investment thesis (is
the market missing the excess-capital story, or is there a reason — asset quality concerns,
management execution risk — the market is discounting the stock that this pure ROE/P-TBV
framework doesn't capture?), not as an automatic "buy" signal — exactly the same caution
applied to the conglomerate discount finding in
[`IB/sum-of-the-parts-conglomerate`](../sum-of-the-parts-conglomerate).
