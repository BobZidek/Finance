# Potential Enhancements

- **Real-world (physical measure) default probability**: recompute Distance-to-Default using
  an estimated real-world expected asset return (via the firm's historical asset return or a
  CAPM-style estimate) instead of the risk-free rate, and compare against the risk-neutral
  probability computed here — quantifying the market price of credit risk.
- **Term structure of default probability**: compute Distance-to-Default and default
  probability across multiple horizons (6 months, 1 year, 3 years, 5 years) to build a full
  default probability term structure per company.
- **Credit spread implied by the model**: back out the credit spread the Merton model implies
  a lender should demand given the computed default probability and an assumed recovery rate
  (reusing recovery assumptions from [`IB/distressed-debt-recovery-waterfall`](../../IB/distressed-debt-recovery-waterfall)),
  and compare against real observed credit spreads if available.
- **Time-varying tracking**: compute Distance-to-Default at multiple historical points leading
  up to a real company's actual default, to show how DD would have deteriorated as an early-warning signal.
- **KMV-style default point convention**: replace the simple total-debt default point with the
  Moody's KMV convention (short-term debt + 0.5 x long-term debt), which better reflects that
  short-term debt is more immediately threatening than long-term debt.
- **Alternative numerical solvers**: compare `fsolve`'s solution against a direct iterative
  fixed-point method, and check solution stability/sensitivity to the initial guess.
- **Real company data**: once live market data access is available, apply this framework to
  real companies' equity market cap, equity volatility, and reported total debt.
