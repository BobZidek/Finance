# Monte Carlo Exotic Option Pricing — Theory

## Why exotics need simulation, not closed-form formulas

[`quant/options-pricing-black-scholes`](../options-pricing-black-scholes) prices vanilla
European options with a closed-form formula, because their payoff depends on only **one**
thing: the underlying's price at expiry. **Path-dependent exotic options** — where the payoff
depends on the underlying's behavior *throughout* its life, not just at the end — generally
have **no closed-form solution**, and Monte Carlo simulation becomes the standard tool: simulate
many possible price paths under the risk-neutral measure, compute the payoff along each path,
average the discounted payoffs, and that average **is** the option's fair value (by the
fundamental theorem of asset pricing, an option's value equals its expected discounted payoff
under the risk-neutral measure).

## Simulating the underlying: same GBM dynamics as vanilla pricing

```
S_(t+dt) = S_t x exp[(r - 0.5 x sigma^2) x dt + sigma x sqrt(dt) x Z],  Z ~ N(0,1)
```

This is exactly the risk-neutral geometric Brownian motion assumption underlying Black-Scholes
itself — the same model, just simulated path-by-path (252 daily steps over a 1-year life here)
instead of solved in closed form.

## Validating the simulation: Monte Carlo must recover the known Black-Scholes price

Before trusting a Monte Carlo pricer on an exotic option with no independently-known answer,
it's essential to validate it on something you **do** know the answer to. This project prices
a **vanilla European call via Monte Carlo** and directly compares it against the
**closed-form Black-Scholes price** — the two should agree, and this project's run confirms
they do: **$11.8128 (Monte Carlo) vs. $11.8370 (closed-form)**, with the closed-form price
falling comfortably inside the Monte Carlo estimate's 95% confidence interval. This is the same
validation discipline as the put-call parity check in the vanilla options project — never trust
a simulation-based pricer without first confirming it reproduces a known answer.

## The Asian option: averaging reduces effective volatility

An **arithmetic-average Asian call** pays `max(Average Price − Strike, 0)`, using the average
price over the option's life rather than just the terminal price. Averaging many correlated but
not-identical daily prices produces a **less volatile** payoff distribution than relying on a
single terminal price — a smoothed average is inherently less likely to land far from its
expected value than a single draw would be. Lower effective volatility directly means a
**cheaper option** (Black-Scholes intuition: option value increases with volatility, so less
effective volatility means less value) — this project's Asian call prices at **$6.6361, a
43.8% discount** to the vanilla call with identical strike and maturity, a substantial and
economically sensible reduction. Asian options are commonly used specifically **because** of
this: a company hedging a commodity purchased steadily throughout a period (not all at once)
naturally wants to hedge its *average* purchase price, not just the price on one specific day.

## The barrier option: knock-out risk destroys value on some paths entirely

An **up-and-out barrier call** behaves exactly like a vanilla call **unless** the underlying's
price ever touches or exceeds the barrier level (here, $130) at any point before expiry — if it
does, the option is immediately "knocked out" and becomes worthless, **regardless of where the
price ends up at expiry**. This project's simulation shows a **28.7% knockout rate** — nearly
30% of simulated paths breach the $130 barrier at some point and pay zero, even if the price
later fell back below the strike-relevant range — producing a **79.6% discount** to the vanilla
call, a far larger discount than the Asian option's, since knockout risk can zero out the
payoff entirely rather than just dampening its variability. Barrier options are cheaper
precisely because the buyer accepts this additional, path-dependent way of losing the entire
premium — useful for investors with a specific view that a price will rise moderately but who
want to pay less for protection against a scenario they consider unlikely or undesirable
(a large rally past the barrier).

## Reading the convergence chart

`output/convergence.png` shows the vanilla Monte Carlo estimate (and its shrinking confidence
interval) as the number of simulated paths grows from 500 to 50,000, converging visibly toward
the closed-form Black-Scholes line. Monte Carlo standard error shrinks proportional to
`1/sqrt(N)` — quadrupling the number of paths only halves the standard error, which is why
achieving high precision via brute-force path count alone gets expensive quickly, and why real
production Monte Carlo pricers invest heavily in variance reduction techniques (see
`ENHANCEMENTS.md`) rather than simply simulating more paths.
