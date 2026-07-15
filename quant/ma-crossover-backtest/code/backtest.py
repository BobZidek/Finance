"""
Moving-Average Crossover Backtest

Backtests a classic trend-following strategy - long when the 50-day SMA
is above the 200-day SMA ("golden cross" regime), flat (cash) otherwise -
against buy-and-hold, across a synthetic 3-year price series with three
distinct regimes (uptrend, choppy/sideways, strong uptrend) designed to
show where trend-following helps and where it hurts.

Run:
    python generate_data.py   (first, if data/synthetic_prices.csv doesn't exist)
    python backtest.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

SHORT_WINDOW = 50
LONG_WINDOW = 200
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.04


def load_prices() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "synthetic_prices.csv")
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SMA_Short"] = df["Close"].rolling(SHORT_WINDOW).mean()
    df["SMA_Long"] = df["Close"].rolling(LONG_WINDOW).mean()
    df["Signal"] = np.where(df["SMA_Short"] > df["SMA_Long"], 1, 0)
    # Trade on the NEXT day's return after a signal change (avoids look-ahead bias)
    df["Position"] = df["Signal"].shift(1).fillna(0)
    return df


def run_backtest(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["DailyReturn"] = df["Close"].pct_change().fillna(0)
    df["StrategyReturn"] = df["Position"] * df["DailyReturn"]
    df["BuyHoldEquity"] = (1 + df["DailyReturn"]).cumprod()
    df["StrategyEquity"] = (1 + df["StrategyReturn"]).cumprod()

    df["TradeChange"] = df["Position"].diff().fillna(0)
    return df


def performance_stats(equity_curve: pd.Series, returns: pd.Series, label: str) -> dict:
    total_days = len(returns)
    total_return = equity_curve.iloc[-1] - 1
    cagr = (equity_curve.iloc[-1]) ** (TRADING_DAYS_PER_YEAR / total_days) - 1

    ann_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    ann_return = returns.mean() * TRADING_DAYS_PER_YEAR
    sharpe = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else float("nan")

    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1
    max_drawdown = drawdown.min()

    return {"Strategy": label, "TotalReturn": total_return, "CAGR": cagr, "AnnVol": ann_vol,
            "Sharpe": sharpe, "MaxDrawdown": max_drawdown}


def plot_equity_curves(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["Date"], df["BuyHoldEquity"], label="Buy & Hold", color="#7FA6D9")
    ax.plot(df["Date"], df["StrategyEquity"], label="SMA(50/200) Crossover", color="#2E5090")
    ax.set_ylabel("Growth of $1")
    ax.set_title("Strategy vs. Buy & Hold Equity Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "equity_curve.png"), dpi=150)
    plt.close(fig)


def plot_price_and_signals(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["Date"], df["Close"], label="Price", color="grey", alpha=0.6)
    ax.plot(df["Date"], df["SMA_Short"], label=f"SMA({SHORT_WINDOW})", color="#C0392B")
    ax.plot(df["Date"], df["SMA_Long"], label=f"SMA({LONG_WINDOW})", color="#2E5090")

    buys = df[df["TradeChange"] == 1]
    sells = df[df["TradeChange"] == -1]
    ax.scatter(buys["Date"], buys["Close"], marker="^", color="green", s=60, label="Buy Signal", zorder=5)
    ax.scatter(sells["Date"], sells["Close"], marker="v", color="red", s=60, label="Sell Signal", zorder=5)

    ax.set_ylabel("Price")
    ax.set_title("Price, Moving Averages, and Trade Signals")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "price_and_signals.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = load_prices()
    df = compute_signals(prices)
    df = run_backtest(df)

    df.round(4).to_csv(os.path.join(OUTPUT_DIR, "backtest_detail.csv"), index=False)

    strategy_stats = performance_stats(df["StrategyEquity"], df["StrategyReturn"], "SMA Crossover")
    buyhold_stats = performance_stats(df["BuyHoldEquity"], df["DailyReturn"], "Buy & Hold")
    stats_df = pd.DataFrame([strategy_stats, buyhold_stats])
    stats_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "performance_summary.csv"), index=False)

    num_trades = int((df["TradeChange"] != 0).sum())
    trades_in_position = df["Position"] == 1
    win_rate = (df.loc[trades_in_position, "StrategyReturn"] > 0).mean()

    with open(os.path.join(OUTPUT_DIR, "backtest_summary.txt"), "w") as f:
        f.write("=== Moving-Average Crossover Backtest ===\n\n")
        f.write(f"Short window: {SHORT_WINDOW} days | Long window: {LONG_WINDOW} days\n")
        f.write(f"Number of position changes (trades): {num_trades}\n")
        f.write(f"Daily win rate while in position: {win_rate:.1%}\n\n")
        f.write(stats_df.round(4).to_string(index=False))
        f.write("\n\n=== By Regime ===\n")
        regime_perf = df.groupby("Regime").apply(
            lambda g: pd.Series({
                "BuyHold_Return": g["DailyReturn"].add(1).prod() - 1,
                "Strategy_Return": g["StrategyReturn"].add(1).prod() - 1,
            }), include_groups=False)
        f.write(regime_perf.round(4).to_string())

    plot_equity_curves(df)
    plot_price_and_signals(df)

    print("=== Moving-Average Crossover Backtest ===")
    print(stats_df.round(4).to_string(index=False))
    print(f"\nNumber of trades: {num_trades}  |  Win rate while in position: {win_rate:.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
