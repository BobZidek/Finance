# Potential Enhancements

- **Duration-matched hedging**: construct a hedge using a different instrument (e.g., a
  Treasury futures position or an offsetting bond) sized to neutralize portfolio duration, and
  test the hedge's effectiveness against a yield shock.
- **Non-parallel curve shocks**: extend the price shock validation beyond parallel shifts to
  steepening/flattening/twist scenarios, using the Key Rate Duration profile to estimate price
  impact under non-parallel curve moves — the real-world use case KRD exists for.
- **OAS and embedded options**: extend to callable/putable bonds, where option-adjusted spread
  (OAS) and effective duration/convexity (computed via valuation under a term structure model,
  not the closed-form formulas used here) are needed instead.
- **Credit spread duration**: separate interest rate duration from credit spread duration for
  corporate bonds, since the two risks can move independently.
- **Real yield curve data**: once live data access is available, build the curve from actual
  Treasury or swap rates and price real bonds off it.
- **Portfolio-level KRD hedge optimization**: solve for a hedge portfolio (using instruments at
  each key maturity) that neutralizes the full KRD profile, not just overall duration - a more
  complete curve-risk-neutral hedge.
- **Bootstrapped curve construction**: replace the simple linear interpolation with a properly
  bootstrapped zero-coupon curve from coupon-bearing par yields, a more realistic construction
  method.
