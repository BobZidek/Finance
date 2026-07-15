# Potential Enhancements

- **Persistent factor exposures**: replace each month's independently-drawn factor scores
  with a slow-moving (autocorrelated) process, more realistic than fresh independent draws
  every month — real value/quality characteristics don't reshuffle completely month to month.
- **Sector/industry neutrality**: add sector tags to the universe and construct the long/short
  portfolio to be sector-neutral (equal sector exposure long and short), a standard real-world
  constraint that prevents the strategy from taking implicit sector bets.
- **Alternative risk management approaches**: compare volatility targeting against a fixed
  gross exposure approach, and against a VaR-budget-based sizing approach (reusing
  [`quant/risk-model-var-cvar`](../risk-model-var-cvar)'s methodology).
- **Factor timing**: instead of a static equal-weighted composite, dynamically adjust factor
  weights based on recent factor performance or macro regime, and evaluate whether timing adds
  value net of the risk of overfitting to recent history.
- **Larger universe and longer history**: extend from 40 stocks/36 months to a much larger
  universe over a longer period, for more statistically robust attribution and performance estimates.
- **Slippage and market impact modeling**: extend the flat per-unit-turnover transaction cost
  to a more realistic model that scales with position size relative to typical trading volume.
- **Real market data**: once live data access is available, replace the synthetic panel with
  real historical fundamental and price data for an actual systematic strategy backtest.
