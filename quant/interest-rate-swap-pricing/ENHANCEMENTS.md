# Potential Enhancements

- **Quarterly/semi-annual payment frequency**: extend from annual to more realistic quarterly
  floating / semi-annual fixed payment schedules, common in real swap conventions.
- **OIS discounting**: use a separate curve for discounting (OIS/SOFR) versus projecting
  floating rate resets (a different index curve), reflecting the post-2008 multi-curve
  framework standard in real swap valuation.
- **Key rate DV01**: decompose overall DV01 into sensitivity to individual points on the curve,
  reusing the Key Rate Duration methodology from
  [`quant/fixed-income-duration-convexity`](../fixed-income-duration-convexity).
- **Swaption pricing**: extend to price an option on the swap (a swaption) using a Black-like
  model, connecting to the option pricing mechanics in
  [`quant/options-pricing-black-scholes`](../options-pricing-black-scholes).
- **Counterparty credit risk (CVA)**: add a Credit Valuation Adjustment reflecting counterparty
  default risk, a material real-world component of swap valuation.
- **Bootstrapped curve from market instruments**: replace the hand-specified zero curve with
  one bootstrapped from actual market deposit rates, futures, and swap rates.
- **Real market data**: once live data access is available, price against a real observed swap
  curve and compare against actual quoted par swap rates.
