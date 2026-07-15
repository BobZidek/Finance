# Fund-Level Model — Capital Calls, Distributions, J-Curve & GP Carry Waterfall

Simulates a 10-year hypothetical buyout fund ("Meridian Growth Partners III") investing in
8 portfolio companies with staggered entry/exit timing. Builds year-by-year capital calls and
gross distributions, runs a running European (whole-fund) waterfall with an 8% preferred
return and 20% GP carry (100% catch-up), and computes fund-level LP Net IRR, DPI, and TVPI —
plus the classic J-curve.

For the theory behind the J-curve and the waterfall mechanics, see
[`theory/fund_waterfall_and_jcurve.md`](theory/fund_waterfall_and_jcurve.md).

## What the code does

1. **Loads fund terms** ([`data/fund_assumptions.csv`](data/fund_assumptions.csv)) — committed
   capital, management fee %, investment period, fund life, carry %, preferred return rate.
2. **Loads the portfolio** ([`data/portfolio_deals.csv`](data/portfolio_deals.csv)) — 8 deals
   with entry year, invested capital, hold period, and deal-level MOIC (a mix of winners and
   one loser, for realism).
3. **Builds year-by-year capital calls** (deal investments + management fees, with the fee
   stepping down from committed capital to remaining unrealized cost after the investment
   period) **and gross distributions** (deal exit proceeds in their exit year).
4. **Runs a running European waterfall**: each year, accrues the 8% preferred return on
   outstanding unreturned capital, then processes that year's distributions through Return of
   Capital → Preferred Return → GP Catch-up → 80/20 Residual Split, tier by tier.
5. **Computes fund-level metrics**: Gross Fund MOIC (deal-level, pre-fee/carry), LP Net
   DPI/TVPI, and **LP Net IRR** (via a manual bisection-search IRR solver on the LP net cash
   flow series — no external finance library required).
6. **Outputs**: a fund summary, portfolio detail CSV, full year-by-year waterfall CSV, a
   J-curve chart, and a capital-calls-vs-distributions bar chart.

## Data note

The fund and all 8 portfolio companies are **fictional/illustrative** — a mechanics
demonstration of fund-level modeling rather than an analysis of a real fund. The waterfall
engine (running preferred-return accrual, GP catch-up math) mirrors a real European
whole-fund waterfall exactly.

## How to run

```bash
cd code
pip install -r requirements.txt
python fund_model.py
```

Outputs are written to `output/`.

## Folder structure

```
fund-model-waterfall/
├── code/
│   ├── fund_model.py
│   └── requirements.txt
├── data/
│   ├── fund_assumptions.csv
│   └── portfolio_deals.csv
├── theory/
│   └── fund_waterfall_and_jcurve.md
├── output/                  # generated summary, waterfall, portfolio detail, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Gross Fund MOIC (deal-level): 1.99x** — what the 8 portfolio companies themselves
  actually returned, combining winners (Deal C at 3.2x) with one loser (Deal E at 0.6x).
- **LP Net TVPI: 1.60x, LP Net IRR: 10.8%** — what LPs actually receive after ~$78.5mm of GP
  carry and years of management fees; the ~0.39x gap versus gross MOIC is the fee-and-carry
  drag of the fund structure itself.
- **Cumulative LP cash flow stays negative through Year 7**, only turning positive in **Year
  8** — a textbook J-curve, and the same year GP carry finally starts flowing (once cumulative
  distributions clear the return-of-capital and preferred-return hurdles).
- **$78.5mm total GP carry earned**, entirely concentrated in Years 8-9 once the whole-fund
  hurdle is cleared — none in the earlier years despite substantial gross distributions,
  illustrating exactly how a European waterfall protects LPs relative to a deal-by-deal structure.
