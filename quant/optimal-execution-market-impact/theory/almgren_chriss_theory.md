# Optimal Execution & Market Impact — Almgren-Chriss Theory

## The core tension: trade fast or trade slow?

Liquidating a large position creates a genuine dilemma. **Trade too fast**, and each trade
moves the price against you — market impact cost. **Trade too slow**, and the unexecuted
position sits exposed to market volatility for longer — timing/holding risk. Almgren & Chriss
(2000) formalized this as a mean-variance optimization over trading *trajectories*, directly
analogous to the mean-variance portfolio optimization in
[`quant/portfolio-optimizer-efficient-frontier`](../portfolio-optimizer-efficient-frontier) —
here the "assets" being traded off are impact cost and timing risk, not different securities.

## The two components of market impact

- **Permanent impact** (`gamma`): each trade moves the price, and that move **persists** —
  it affects the cost of every subsequently-traded share. Depends only on total shares traded,
  not on how fast you trade them.
- **Temporary impact** (`eta`): each trade also incurs a cost proportional to the **rate** of
  trading (shares per period) that **reverts** after the trade — this is the cost lever that
  actually rewards trading more slowly, since spreading the same total volume over more periods
  reduces the per-period trading rate, and impact cost is quadratic (`v^2`) in that rate.

```
Expected Cost = 0.5 x gamma x X^2 + eta_tilde x SUM(v_t^2)
```

The permanent-impact term is fixed regardless of trajectory (it only depends on total shares
`X`); the temporary-impact term is what the optimization actually controls, by choosing how to
split `X` into a sequence of trades `v_t`.

## The optimal trajectory: a hyperbolic sine, not a straight line

```
x_j = X x sinh(kappa x (N-j)) / sinh(kappa x N)         (shares remaining after period j)
kappa = sqrt(risk_aversion x sigma^2 / eta_tilde)
```

A **naive TWAP** (Time-Weighted Average Price) strategy trades the same amount every period —
a straight-line trajectory. The Almgren-Chriss optimal trajectory is a **hyperbolic sine
curve** that **front-loads trading** (trades faster early, tapering off later) whenever risk
aversion is positive — reducing the position (and its exposure to volatility risk) faster than
TWAP would, at the cost of somewhat higher market impact from the faster early trading. As
`kappa -> 0` (risk aversion approaches zero — a trader who only cares about minimizing expected
cost, not risk), the optimal trajectory **converges exactly to TWAP** — this project's code
includes that limiting case explicitly, and it's confirmed by the efficient frontier data
(`output/efficient_frontier.csv`), which shows the lowest-risk-aversion row landing very close
to the pure-TWAP benchmark's cost and risk figures.

## Reading this project's three-strategy comparison

| Strategy | Expected Cost | Cost Std Dev (risk) |
|---|---|---|
| Almgren-Chriss Optimal | $13,850 | $116,789 |
| TWAP (naive linear) | $7,250 | $253,229 |
| Immediate Liquidation | $50,000 | $0 |

This is **not** a case where one strategy dominates the others — it's a genuine trade-off,
exactly as intended. **TWAP has the lowest expected cost but by far the highest risk** (spread
evenly, but exposed to volatility for the full horizon). **Immediate liquidation has zero risk
(nothing is left unexecuted after period one) but by far the highest expected cost** (all
market impact concentrated into a single large trade). **The Almgren-Chriss optimal strategy
sits between them** — at this project's chosen risk aversion, it accepts roughly $6,600 more
expected cost than TWAP in exchange for cutting cost risk by more than half — a genuinely
better risk-adjusted outcome for a risk-averse trader, not simply "cheaper" or "safer" in
isolation.

## The efficient frontier — the real deliverable

Just as the mean-variance optimizer sweeps target returns to trace the Markowitz frontier, this
project sweeps **risk aversion** (`lambda`) across many orders of magnitude to trace the
**execution efficient frontier**: `output/efficient_frontier.png` shows expected cost rising
smoothly from ~$7,271 (near-TWAP, minimal risk aversion) to $50,000 (near-immediate
liquidation, extreme risk aversion) as cost standard deviation falls correspondingly from
~$244,432 toward $0 — a clean, monotonic trade-off curve, letting a trading desk choose the
point on the frontier matching their actual risk tolerance, rather than being stuck picking
between only TWAP and immediate execution as binary extremes.
