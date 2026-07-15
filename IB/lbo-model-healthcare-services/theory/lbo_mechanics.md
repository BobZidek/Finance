# Leveraged Buyout (LBO) — Theory

## What it is

An LBO is the acquisition of a company financed predominantly with debt, where the acquirer
(a private equity sponsor) puts in a relatively small equity check and uses the target's own
future cash flow to service and pay down the debt over the hold period. Returns come from
three levers: **debt paydown** (deleveraging increases the equity slice of enterprise value
over time even if EV doesn't change), **EBITDA growth**, and **multiple expansion/contraction**
at exit. Healthcare services roll-ups (dental, veterinary, urgent care) are a classic LBO
target: fragmented, recurring-revenue, cash-generative businesses that support meaningful
leverage.

## Step 1 — Sources & Uses

```
Uses = Entry Enterprise Value (Entry Multiple x EBITDA) + Transaction Fees
Sources = Term Loan + Subordinated Notes + Sponsor Equity  (must equal Uses)
```

Debt is sized in "turns" of EBITDA (e.g. "4.0x Term Loan, 1.5x Subordinated Notes" = 5.5x
total leverage) rather than as a fixed dollar amount, because lenders underwrite based on the
company's cash flow capacity relative to EBITDA. **Sponsor equity is the plug** — whatever's
left after debt sources cover as much of the purchase price as leverage will support.

## Step 2 — The debt schedule (the engine of an LBO)

Each year:

```
NOPAT-style build: EBITDA − D&A = EBIT
EBIT − Interest Expense = EBT
EBT × (1 − Tax Rate) ... = Net Income
Net Income + D&A − Capex − ΔNWC = Free Cash Flow available for debt service
```

That free cash flow is used, in order, for:
1. **Mandatory amortization** — a fixed % of the original Term Loan balance required
   contractually each year (typically 1-10%/year, senior debt only — subordinated/high-yield
   debt is usually interest-only/"bullet" until maturity, as modeled here).
2. **Cash flow sweep** — a portion (often 50-100%) of *remaining* free cash flow after
   mandatory amortization is used to pay down debt early, senior tranches first (the
   "waterfall"). This is why leverage typically falls fast in years 1-2 of a healthy LBO.

Interest expense is calculated on the **beginning-of-year** balance of each tranche, so
interest declines each year as the sweep pays down principal — a compounding effect that
accelerates deleveraging.

## Step 3 — Exit and returns

```
Exit Enterprise Value = Exit Multiple × Final-Year EBITDA
Exit Equity Value = Exit Enterprise Value − Remaining Total Debt at Exit
MOIC (Multiple on Invested Capital) = Exit Equity Value / Entry Sponsor Equity
IRR = MOIC^(1 / Hold Period Years) − 1     (valid when there are no interim distributions)
```

## The three return levers, explicitly

1. **Deleveraging**: even at a *flat* entry/exit multiple (both 10.0x in the base case here),
   returns are strongly positive because the debt balance shrinks from $330mm to $202.7mm over
   5 years — that difference flows entirely to the equity holder at exit.
2. **EBITDA growth**: EBITDA grows from $60mm to $95.5mm (revenue growth + margin expansion),
   which directly increases exit EV at any given multiple.
3. **Multiple expansion/contraction**: the sensitivity grid shows how sensitive returns are to
   paying a lower entry multiple or achieving a higher exit multiple — moving from paying
   11.0x down to 9.0x at entry (holding a 10.0x exit) moves IRR from ~17.0% to ~27.8%.

## Why the sensitivity grid matters

LBO returns are highly path-dependent on two things a sponsor doesn't fully control: what they
pay (competitive process) and what they can sell for (market conditions years later). The
Entry Multiple × Exit Multiple IRR grid is the standard way to show an investment committee
the range of outcomes, and to identify the **entry price ceiling** for hitting a target return
threshold (many PE funds have a hard ~20-25% IRR hurdle) — in this model, entry above ~10.5x
starts to push IRR below a 20% hurdle even at a flat-to-favorable exit.
