# REIT Net Asset Value (NAV) Valuation — Theory

## Why REITs get their own valuation framework

REITs (Real Estate Investment Trusts) own portfolios of income-producing real estate and are
required to distribute most of their taxable income as dividends. Two things break the standard
EV/EBITDA or DCF toolkit used elsewhere in this repo: (1) **real estate's most useful valuation
signal is the market's own pricing of similar properties (cap rates)**, not a peer company
multiple, and (2) **GAAP depreciation on real estate is often economically misleading** — real
estate frequently *appreciates*, unlike most operating assets, so heavy GAAP D&A charges can
make a REIT's net income look far weaker than its actual cash-generating capacity.

## The NAV approach — building value property by property

```
Property Value = Net Operating Income (NOI) / Market Cap Rate
```

A **cap rate** is simply the current yield the market demands for a given property type and
quality — a lower cap rate means the market is willing to pay *more* per dollar of NOI (safer,
more desirable properties), and a higher cap rate means the market pays *less* (riskier or
less desirable properties). This project's portfolio shows exactly that pattern: **Grocery-
Anchored Centers (6.25% cap rate, the lowest) command the highest value per dollar of NOI**,
reflecting their defensive, recession-resistant tenant base (grocery stores drive reliable
foot traffic), while **Power Centers (7.50%, the highest cap rate)** — often more exposed to
big-box retail vacancy risk — are valued more conservatively per dollar of NOI, even though
their NOI is meaningfully smaller.

```
NAV to Common = Sum of Property Values + Cash/Other Investments − Total Debt − Preferred Equity
NAV per Share = NAV to Common / Diluted Shares Outstanding
```

This project's REIT: **$2,404.4mm total real estate value**, **$14.52 NAV per share** after
netting debt and preferred equity — a bottom-up, asset-by-asset valuation entirely independent
of the stock's current trading price.

## Cap rate sensitivity — the REIT equivalent of bond duration

Just as a bond's price is highly sensitive to yield changes (see
[`quant/fixed-income-duration-convexity`](../../quant/fixed-income-duration-convexity)), a
REIT's NAV is highly sensitive to cap rate movements — and for the same underlying reason: both
are essentially valuing a stream of future cash flows using a market-clearing discount rate.
`output/cap_rate_sensitivity.png` shows NAV per share swinging materially across a ±100bp
shift in cap rates applied uniformly across the portfolio — a genuinely important risk factor
for REIT investors, since cap rates move with broader interest rates and real estate market
sentiment, not with the REIT's own operating performance.

## FFO — the REIT-specific earnings metric

```
FFO (Funds From Operations) = Net Income + Real Estate Depreciation & Amortization
```

FFO adds back real estate D&A specifically because GAAP depreciation assumes real estate
**loses** value over time (the standard accounting treatment for most fixed assets), while in
practice, well-located, well-maintained real estate frequently **holds or gains** value. FFO is
the REIT industry's standard "cash earnings" proxy — the REIT equivalent of EBITDA or adjusted
earnings — and **P/FFO is the REIT-specific P/E**, used alongside (not instead of) NAV.

## Why NAV and P/FFO can (and should) be checked against each other

This project's two independent approaches **agree directionally**: the stock trades at an
**11.8% discount to NAV** and an even wider **18.9% discount to its P/FFO-implied value**. Two
independent valuation methods pointing the same direction is a meaningfully stronger signal
than either alone — if the two methods disagreed sharply (e.g., trading above NAV but below
P/FFO-implied value), that divergence itself would be the more interesting analytical finding,
often pointing to a specific disagreement between how the market is pricing the underlying real
estate versus how it's pricing the REIT's operating/leverage profile. Real REIT equity research
routinely triangulates both approaches for exactly this reason.
