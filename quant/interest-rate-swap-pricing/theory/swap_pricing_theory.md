# Interest Rate Swap Pricing — Theory

## What a swap is, and why it needs a discount curve, not a single rate

A plain-vanilla interest rate swap exchanges a **fixed** stream of payments for a **floating**
stream, both on the same notional, with no exchange of principal. Pricing it correctly requires
the **entire discount curve**, not a single yield — this project builds directly on the
curve-construction mechanics from
[`quant/fixed-income-duration-convexity`](../fixed-income-duration-convexity), applying them
to a derivative instead of a bond.

```
Discount Factor(t) = 1 / (1 + ZeroRate(t))^t
```

## Forward rates: what the floating leg is expected to pay

The floating leg's future payments aren't known today — they'll be set by whatever the
reference rate actually is on each future reset date. But under no-arbitrage pricing, the
**expected** floating payment for any future period is exactly the **forward rate** implied by
today's discount curve for that period:

```
Forward Rate for period [t-1, t] = DiscountFactor(t-1) / DiscountFactor(t) - 1
```

This project's curve shows forward rates diverging from the zero rate curve — a
directly-observable consequence of the humped curve shape used here (rates dip in the middle
years before rising again), since forward rates are inherently more sensitive to the curve's
local slope than the zero rates themselves.

## Two independent ways to value the floating leg — cross-checked against each other

```
Shortcut method: Floating Leg PV = Notional x (1 - Final Discount Factor)
Manual method: Floating Leg PV = SUM(Forward Rate_t x Notional x Discount Factor_t)
```

These are two genuinely different-looking formulas that must produce the **same answer** for
any correctly-built curve — the shortcut is a well-known closed-form identity that telescopes
out of the manual forward-rate summation. This project computes **both independently and
verifies they agree to within floating-point precision** (a difference on the order of 1e-15,
the same verification standard used for put-call parity in
[`quant/options-pricing-black-scholes`](../options-pricing-black-scholes)) — strong evidence
the curve and forward rate mechanics are implemented correctly.

## The par swap rate — where a brand-new swap starts

```
Par Swap Rate = (1 - Final Discount Factor) / SUM(Discount Factors)
```

A swap entered into **today** at the par rate has **zero NPV** to either party — neither side
pays anything upfront, since the fixed and floating legs are worth exactly the same. This
project's par rate (4.1952%) is verified directly: pricing the swap at exactly this rate
produces an NPV of effectively zero (`output/swap_pricing_summary.txt` shows this check
explicitly).

## Marking an existing (off-market) swap to market

A swap entered into in the **past**, at a fixed rate that no longer matches today's par rate,
has **nonzero value** to one party — this is exactly the situation for any swap sitting on a
balance sheet after rates have moved since inception:

```
NPV to Fixed-Rate Payer = Floating Leg PV − Fixed Leg PV (at the swap's contractual rate)
```

This project's existing swap has a **contractual fixed rate of 3.80%, below the current par
rate of 4.1952%** — meaning the fixed-rate payer is locked into paying *less* than what a new
swap would cost them today, a real economic benefit worth **$1.75mm** on $100mm notional. If
this position needed to be closed out or transferred, this NPV is exactly what would change
hands.

## DV01: how much does the swap's value move with rates?

```
DV01 = NPV(curve shifted +1bp) − NPV(curve shifted −1bp), divided by 2
```

This project reports DV01 as **+$0.0438mm per 1bp of parallel rate increase** — a positive
number, meaning **the fixed-rate payer's position gains value as rates rise**. This makes
intuitive economic sense: the payer keeps paying a fixed 3.80% regardless of where rates go,
while the floating leg they *receive* becomes more valuable as rates rise — so a rate increase
benefits them on both sides of the position simultaneously. This project reports DV01
explicitly with its sign and direction stated in plain language, specifically because sign
convention confusion (is DV01 "value gained on a rate increase" or "value lost on a rate
decrease," and for which party?) is one of the most common sources of real trading-desk
communication errors around interest rate risk.
