# Potential Enhancements

- **Monte Carlo across many simulated paths**: run the same strategy across hundreds of
  independently simulated price paths (not just one) and report the distribution of outcomes,
  since a single backtest (this project included) has a very limited sample size.
- **Warmup-aware comparison**: re-run the buy-and-hold benchmark starting only from the day
  the SMA(200) first becomes valid, isolating "is the rule good" from "how much data does the
  rule need before it can act."
- **Parameter sensitivity**: sweep the short/long window lengths (e.g. 20/100, 50/150, 50/200)
  and show how sensitive results are to the specific choice used here.
- **Transaction costs and slippage**: add realistic per-trade costs (even though only 3 trades
  occurred here, a shorter-window variant would trade far more often and costs would matter a
  lot more).
- **Long/short variant**: extend from long/flat to long/short (short when SMA(50) < SMA(200))
  and compare risk/return against the long/flat version.
- **Real historical data**: replace the synthetic price series with real historical OHLCV data
  once live market data access is available, and compare results.
- **Alternative trend filters**: compare the SMA crossover against other trend-following
  signals (EMA crossover, MACD, Donchian channel breakout) on the same synthetic data.
