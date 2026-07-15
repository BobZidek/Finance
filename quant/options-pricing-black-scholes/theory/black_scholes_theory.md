# Black-Scholes Options Pricing & Greeks — Theory

## What the model prices, and its core assumption

The Black-Scholes-Merton model prices **European options** (exercisable only at expiration,
unlike American options which can be exercised any time) under the assumption that the
underlying's price follows **geometric Brownian motion** — continuous trading, constant
volatility and risk-free rate, no dividends, no transaction costs. Real markets violate every
one of these assumptions to some degree, which is exactly why Black-Scholes is a starting
point for options pricing, not the final word (see the theory note on implied volatility below).

## The formula

```
d1 = [ln(S/K) + (r + sigma^2/2) x T] / (sigma x sqrt(T))
d2 = d1 - sigma x sqrt(T)

Call Price = S x N(d1) - K x e^(-rT) x N(d2)
Put Price  = K x e^(-rT) x N(-d2) - S x N(-d1)
```

Where `N(.)` is the standard normal cumulative distribution function. Intuitively: `N(d1)` and
`N(d2)` are risk-adjusted probabilities that the option finishes in-the-money, and the formula
is essentially "expected discounted payoff under the risk-neutral measure" — the same idea as
a DCF, but for a payoff that depends non-linearly on a random future price rather than a
deterministic cash flow.

## The Greeks — what each one actually measures

| Greek | Measures | This project's Call/Put results |
|---|---|---|
| **Delta** | Change in option price per $1 change in spot | Call: 0.47, Put: -0.53 — a $1 move in spot moves the call ~$0.47 and the put ~-$0.53 |
| **Gamma** | Change in Delta per $1 change in spot (same for call & put) | 0.0225 — Delta itself becomes less accurate for large spot moves; Gamma quantifies that |
| **Vega** | Change in option price per 1 percentage-point change in volatility | 0.28 (same for call & put) — a 1pt vol increase adds ~$0.28 to either option |
| **Theta** | Change in option price per day, holding everything else constant ("time decay") | Call: -0.024/day, Put: -0.013/day — both options lose value as expiration approaches |
| **Rho** | Change in option price per 1 percentage-point change in the risk-free rate | Call: +0.21, Put: -0.31 — calls gain value, puts lose value, as rates rise |

Delta and Gamma are the most commonly used for **hedging** — a market maker holding a short
option position typically hedges by holding `Delta` shares of the underlying (delta-hedging),
and Gamma measures how often that hedge needs to be rebalanced as the underlying moves.

## Why the Delta/Gamma/Vega charts have the shape they do

- **Delta approaches 1.0 (call) or -1.0 (put) deep in-the-money**, and approaches 0 deep
  out-of-the-money — an option that's certain to finish in-the-money behaves like owning (or
  shorting) the stock outright; an option certain to expire worthless has no price sensitivity
  to the underlying at all.
- **Gamma peaks near the strike price ($105 here)** and falls off on both sides — this is
  exactly where Delta is changing fastest (transitioning from ~0 to ~1), and exactly why
  at-the-money options are the hardest to hedge (Gamma risk is highest there).
- **Vega also peaks near the strike** for the same underlying reason: at-the-money options have
  the most "optionality" — genuine uncertainty about whether they'll finish in or out of the
  money — so a change in volatility has the largest proportional effect on their value there.

## Put-call parity as a built-in correctness check

```
Call Price − Put Price = Spot Price − Present Value of Strike (K x e^(-rT))
```

This relationship must hold for *any* correctly-implemented Black-Scholes pricer, independent
of the specific inputs, because it follows from a pure no-arbitrage argument (a portfolio of
long call + short put has an identical payoff to a forward contract, regardless of the pricing
model used) — not from the Black-Scholes assumptions specifically. This project verifies the
relationship explicitly (`output/black_scholes_summary.txt`), and it holds to within floating-
point precision (a difference on the order of 1e-15) — strong evidence the call and put
formulas were implemented correctly and consistently, not just individually "reasonable-looking."

## Why implied volatility matters more in practice than model price

In real markets, traders rarely use Black-Scholes to compute "the correct price" from an
assumed volatility — instead, they observe the **market price** and back out the **implied
volatility** that would make the formula match it. Because real markets exhibit a "volatility
smile/skew" (implied vol differs by strike, which pure Black-Scholes assumes is impossible),
the model is used more as a **standardized quoting convention** for options prices than as a
literal statement about correct value — a nuance worth understanding even though this project
only implements the forward pricing direction (see `ENHANCEMENTS.md`).
