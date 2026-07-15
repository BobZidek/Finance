# Discounted Cash Flow (DCF) Valuation — Theory

## What it is

A DCF estimates a company's **intrinsic value** as the present value of the cash it will
generate in the future. Unlike comps (market-relative pricing), a DCF doesn't depend on how
the market is currently pricing peers — it's built entirely from the company's own projected
cash flows and a required rate of return. In practice it's used as the intrinsic anchor
against which comps and precedent transaction ranges are checked.

## The mechanics, step by step

### 1. Forecast Unlevered Free Cash Flow (UFCF)

UFCF is the cash the business generates before financing decisions (debt/equity) — it belongs
to *all* capital providers, which is why it's discounted at WACC (a blended cost of capital)
rather than just the cost of equity.

```
Revenue × EBIT Margin           = EBIT
EBIT × (1 − Tax Rate)           = NOPAT   (Net Operating Profit After Tax)
NOPAT + D&A − Capex − ΔNWC      = Unlevered Free Cash Flow
```

- **D&A is added back** because it's a non-cash expense that reduced EBIT but didn't use cash.
- **Capex is subtracted** because it's a real cash outflow that doesn't hit the income statement directly.
- **ΔNWC (change in net working capital)** captures cash tied up in receivables/inventory
  growth net of payables — a growing business typically consumes cash here.

### 2. Discount rate — WACC via CAPM

```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium        (CAPM)
After-Tax Cost of Debt = Pre-Tax Cost of Debt × (1 − Tax Rate)
WACC = (E / (D+E)) × Cost of Equity + (D / (D+E)) × After-Tax Cost of Debt
```

WACC is the blended return required by both shareholders and lenders — it's the "hurdle rate"
future cash flows must clear to create value, and the rate used to discount every projected
cash flow back to present value.

### 3. Terminal Value

Forecasting cash flows forever is impossible, so after the explicit forecast period (5 years
here), a **terminal value** captures all cash flows beyond that, using the Gordon Growth
(perpetuity growth) formula:

```
Terminal Value = FCF_final year × (1 + g) / (WACC − g)
```

`g` is a long-run sustainable growth rate — typically close to long-run GDP/inflation
(2-3%), since no company can outgrow the economy forever without becoming the entire economy.
The terminal value is then discounted back to present value using the same final-year discount
factor as the last explicit forecast year.

### 4. Enterprise Value → Equity Value → Share Price

```
Enterprise Value = Σ PV(explicit-period UFCF) + PV(Terminal Value)
Equity Value      = Enterprise Value − Net Debt
Implied Share Price = Equity Value / Diluted Shares Outstanding
```

## Why sensitivity tables matter

A DCF is extremely sensitive to two assumptions that are inherently uncertain: **WACC** and
**terminal growth rate**. A ±1% swing in either can move the implied value by 20-30%+. That's
why the standard output isn't a single number — it's a **sensitivity (data table) grid** of
implied share price across a WACC × terminal growth matrix, so the reader can see the range
of reasonable outcomes rather than a false-precision point estimate.

## Key critique built into this project

In the run included here, **~75% of Enterprise Value comes from the terminal value**, not
the explicit 5-year forecast. This is normal — but it's also the central criticism of DCF:
most of the valuation rests on an assumption about growth *decades* from now, which is
inherently the least reliable part of the model. Always check what % of EV comes from the
terminal value; if it's very high (>75-80%), the explicit forecast period may be too short,
or the business may not be mature enough for a stable perpetuity assumption yet.
