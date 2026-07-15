# Potential Enhancements

- **Implied volatility solver**: given a market option price, back out the implied volatility
  via a root-finder (Newton-Raphson or bisection on the Black-Scholes formula) — the direction
  practitioners actually use the model in, as discussed in the theory doc.
- **Volatility smile/skew**: model implied volatility as a function of strike (and expiry) to
  reflect real market pricing, rather than assuming a single flat volatility.
- **American option pricing**: implement a binomial tree or finite-difference method to price
  American options (early exercise), and compare against the European Black-Scholes price to
  quantify the early-exercise premium.
- **Dividend adjustment**: extend the formula to handle a continuous dividend yield (or
  discrete dividend payments) on the underlying.
- **Monte Carlo pricing cross-check**: price the same option via Monte Carlo simulation of the
  underlying's terminal price distribution and confirm convergence to the closed-form
  Black-Scholes price as the number of simulated paths grows.
- **Exotic options**: extend to price simple exotic structures (digital/binary options,
  barrier options) where closed-form or semi-analytical solutions exist.
- **Real market data calibration**: once live options market data is reachable, calibrate
  against real quoted prices and implied volatilities for an actual underlying.
