# Mean-Variance Portfolio Optimization — Theory

## The Markowitz framework

Modern Portfolio Theory (Markowitz, 1952) formalizes portfolio construction as a trade-off
between expected return and risk (variance), exploiting the fact that **combining imperfectly
correlated assets reduces portfolio risk below the weighted average of the individual assets'
risks** — diversification is a genuine free lunch, up to the limits of the available
correlation structure.

```
Portfolio Return  = w^T x mu           (weighted average of expected returns)
Portfolio Variance = w^T x Cov x w      (depends on the FULL covariance matrix, not just
                                          individual variances - this is where diversification
                                          benefit comes from)
```

## Building the efficient frontier

For a range of target returns, the frontier is built by **solving a constrained optimization
problem** at each target: minimize portfolio variance subject to (1) weights summing to 100%
and (2) achieving that specific target return, with weights bounded between 0% and 100%
(long-only, no leverage or short-selling — the standard simplification for a first pass).
This project uses `scipy.optimize.minimize` (SLSQP, a gradient-based solver that handles
equality and inequality constraints) rather than a closed-form solution, since long-only
bounds don't have one — a defensible, standard numerical approach.

## Two portfolios worth naming specifically

- **Global Minimum Variance (GMV)**: the single portfolio with the lowest possible volatility,
  regardless of return — the leftmost point on the frontier.
- **Maximum Sharpe Ratio (Tangency) Portfolio**: the portfolio that maximizes
  `(Return - Risk-Free Rate) / Volatility` — the point where a line from the risk-free rate is
  tangent to the frontier. This is the portfolio of *risky assets* that, combined with
  varying amounts of the risk-free asset, produces the best possible risk-adjusted return at
  *any* risk level — the theoretical basis for the **Capital Market Line** plotted alongside
  the frontier.

## Why several assets get exactly 0% weight — and why that's normal, not a bug

In this project's output, **International Developed Equity, Emerging Markets Equity, and
REITs all receive 0% weight** in both the GMV and Tangency portfolios. This is a well-known,
structural property of mean-variance optimization, not a modeling error: **an asset gets
excluded whenever another asset (or combination of assets) offers equal or better return per
unit of *marginal* risk contribution**, given the full correlation structure — not because the
excluded asset is individually "bad." Here, US Large Cap and Small Cap Equity's high
correlation with International Developed (0.80, 0.70) means International Developed offers
little diversification benefit that US equities don't already provide, while carrying similar
risk — so the optimizer allocates the "equity risk budget" to the assets already in the
portfolio rather than adding a highly correlated near-substitute.

**This "corner solution" tendency is one of the most cited practical critiques of naive
mean-variance optimization** — it tends to produce concentrated, unintuitive portfolios that
ignore assets a real allocator might want for qualitative diversification reasons, and is
notoriously sensitive to small changes in the input assumptions (expected returns especially).
See `ENHANCEMENTS.md` for standard fixes (position limits, Black-Litterman, resampling).

## Reading this project's frontier

- **GMV portfolio**: 5.06% expected return, 5.41% volatility, dominated by US Investment Grade
  Bonds (82.7% weight) — bonds' low volatility and near-zero/negative correlation with equities
  make them the natural anchor for minimizing risk.
- **Tangency portfolio**: 7.63% expected return, 10.21% volatility, Sharpe ratio 0.36 (the best
  achievable in this universe) — a more balanced mix of equities, bonds, and high yield credit.
- The **Capital Market Line** shows that for *any* target risk level, combining the risk-free
  asset with the Tangency portfolio (rather than any other point on the risky-asset frontier)
  produces a strictly better risk-adjusted outcome — the core insight of the Capital Asset
  Pricing Model (CAPM) that follows directly from this framework.
