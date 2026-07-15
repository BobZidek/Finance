# Revolver Mechanics & Exit Timing — Theory

## Why a revolver, when a Term Loan already exists

A **revolving credit facility (revolver)** is a standing line of credit — undrawn at close,
available to be drawn and repaid flexibly over the life of the deal. Unlike the Term Loan
(a fixed amount drawn entirely at close), the revolver exists specifically to **absorb
short-term cash flow volatility**: a bad working capital swing, a temporary EBITDA dip, or a
seasonal cash crunch that would otherwise force a distressed asset sale or a missed debt
payment. Lenders price it favorably relative to that flexibility, and sponsors size it (here,
$20mm, roughly a third of a typical year's EBITDA) based on how volatile the business's cash
flow realistically is.

## The waterfall priority, and why revolver comes first

Each year, available cash is allocated in a specific order:

```
1. Mandatory Term Loan amortization      (contractual, happens regardless of cash available)
2. Revolver paydown                       (if drawn - repay the most flexible, shortest-tenor debt first)
3. Term Loan cash sweep                   (optional prepayment of the largest tranche)
4. Subordinated Notes paydown             (only after the Term Loan is fully repaid - it's junior)
```

If free cash flow after mandatory amortization is **negative** in a given year, the model
**draws the revolver** to cover the shortfall rather than triggering a payment default — this
is exactly the scenario the facility exists for. If cash is **positive**, any outstanding
revolver balance gets repaid *before* any optional Term Loan prepayment, since revolver
interest (and an ongoing commitment fee on the undrawn portion) makes carrying a revolver
balance the least efficient use of excess cash.

## Reading this project's result: revolver never draws

In the base-case run here, **the revolver is never drawn** — free cash flow is positive
every year of the 7-year forecast. That's not a modeling failure; it's the expected outcome
for a base case built on reasonably healthy growth and margin assumptions. The revolver's
value in this model is as **downside protection that doesn't show up in the base case at
all** — its presence matters for the scenarios where growth stalls or working capital swings
unfavorably (see `ENHANCEMENTS.md` for a stress-test scenario that actually draws it). A real
lender underwriting this deal cares about revolver capacity precisely *because* it's meant to
sit unused in the base case.

## The MOIC vs. IRR tradeoff across exit years

This project's key output is a direct comparison of sponsor returns at three candidate exit
years (3 / 5 / 7) from the same underlying forecast:

| Exit Year | MOIC | IRR |
|---|---|---|
| 3 | 1.88x | 23.3% |
| 5 | 2.58x | 20.9% |
| 7 | 3.38x | 19.0% |

**MOIC rises monotonically with a longer hold** (more years for EBITDA growth and debt
paydown to compound), but **IRR falls** — because IRR annualizes the return, and stretching
the same multiple of invested capital over more years lowers the annualized rate even as the
total dollar return grows. This is one of the most important practical tensions in PE exit
timing: a fund nearing the end of its investment period (needing to return capital to LPs on
a specific schedule, and reporting quarterly IRR marks) may prefer the faster, higher-IRR
3-year exit; a fund with a longer runway and a mandate to maximize absolute dollar proceeds
may prefer holding to year 7. Neither is "more correct" — the right answer depends on the
fund's own liquidity needs and reporting incentives, which is exactly why real exit-timing
decisions weigh both metrics rather than optimizing for one alone.
