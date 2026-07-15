"""
Pairs Trading / Statistical Arbitrage with Cointegration Testing

Tests whether two synthetic assets are cointegrated (Engle-Granger
two-step method: OLS hedge ratio, then Augmented Dickey-Fuller test on
the residual spread, cross-checked against statsmodels' direct coint()
test), then trades the z-scored spread with a standard mean-reversion
rule: enter when the spread is 2 standard deviations from its mean, exit
when it reverts to within 0.5 standard deviations.

Run:
    python generate_data.py   (first, if data/pair_prices.csv doesn't exist)
    python pairs_trading_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

ENTRY_Z = 2.0
EXIT_Z = 0.5
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.04


def load_prices() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "pair_prices.csv"), parse_dates=["Date"])


def engle_granger_test(log_a: pd.Series, log_b: pd.Series) -> dict:
    X = sm.add_constant(log_b)
    ols_result = sm.OLS(log_a, X).fit()
    hedge_ratio = ols_result.params.iloc[1]
    intercept = ols_result.params.iloc[0]

    residual_spread = log_a - hedge_ratio * log_b - intercept
    adf_stat, adf_pvalue, *_ = adfuller(residual_spread, autolag="AIC")

    coint_stat, coint_pvalue, _ = coint(log_a, log_b)

    return {
        "hedge_ratio": hedge_ratio, "intercept": intercept, "residual_spread": residual_spread,
        "adf_stat": adf_stat, "adf_pvalue": adf_pvalue,
        "coint_stat": coint_stat, "coint_pvalue": coint_pvalue,
    }


def build_zscore(spread: pd.Series) -> pd.Series:
    return (spread - spread.mean()) / spread.std()


def generate_positions(z: pd.Series) -> pd.Series:
    """+1 = long the spread (long A, short B*hedge_ratio); -1 = short the spread; 0 = flat.
    Enters at |z| > ENTRY_Z, exits when |z| < EXIT_Z, otherwise holds the existing position."""
    position = 0
    positions = []
    for val in z:
        if position == 0:
            if val > ENTRY_Z:
                position = -1
            elif val < -ENTRY_Z:
                position = 1
        else:
            if abs(val) < EXIT_Z:
                position = 0
        positions.append(position)
    return pd.Series(positions, index=z.index)


def run_backtest(df: pd.DataFrame, hedge_ratio: float) -> pd.DataFrame:
    df = df.copy()
    df["ReturnA"] = df["Price_A"].pct_change().fillna(0)
    df["ReturnB"] = df["Price_B"].pct_change().fillna(0)

    # Spread return: long A, short hedge_ratio units of B (dollar-neutral-ish spread trade)
    df["SpreadReturn"] = df["ReturnA"] - hedge_ratio * df["ReturnB"]

    # Trade on the prior day's position to avoid look-ahead bias
    df["PositionLag"] = df["Position"].shift(1).fillna(0)
    df["StrategyReturn"] = df["PositionLag"] * df["SpreadReturn"]
    df["StrategyEquity"] = (1 + df["StrategyReturn"]).cumprod()
    return df


def performance_stats(returns: pd.Series, equity: pd.Series) -> dict:
    total_days = len(returns)
    ann_return = returns.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else float("nan")
    running_max = equity.cummax()
    max_drawdown = (equity / running_max - 1).min()
    return {"TotalReturn": equity.iloc[-1] - 1, "AnnReturn": ann_return, "AnnVol": ann_vol,
            "Sharpe": sharpe, "MaxDrawdown": max_drawdown}


def plot_prices_and_spread(df: pd.DataFrame, spread: pd.Series, z: pd.Series):
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    axes[0].plot(df["Date"], df["Price_A"], label="Asset A", color="#2E5090")
    axes[0].plot(df["Date"], df["Price_B"], label="Asset B", color="#C0392B")
    axes[0].set_title("Price Series")
    axes[0].legend(fontsize=8)

    axes[1].plot(df["Date"], spread, color="#1E8449")
    axes[1].axhline(spread.mean(), color="grey", linestyle="--", linewidth=1)
    axes[1].set_title("Cointegrating Residual Spread")

    axes[2].plot(df["Date"], z, color="#7FA6D9")
    axes[2].axhline(ENTRY_Z, color="#C0392B", linestyle="--", linewidth=1, label=f"Entry (+/-{ENTRY_Z})")
    axes[2].axhline(-ENTRY_Z, color="#C0392B", linestyle="--", linewidth=1)
    axes[2].axhline(EXIT_Z, color="grey", linestyle=":", linewidth=1, label=f"Exit (+/-{EXIT_Z})")
    axes[2].axhline(-EXIT_Z, color="grey", linestyle=":", linewidth=1)
    axes[2].set_title("Spread Z-Score with Entry/Exit Bands")
    axes[2].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "prices_spread_zscore.png"), dpi=150)
    plt.close(fig)


def plot_equity_curve(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["StrategyEquity"], color="#2E5090")
    ax.axhline(1.0, color="grey", linestyle="--", linewidth=1)
    ax.set_ylabel("Growth of $1")
    ax.set_title("Pairs Trading Strategy Equity Curve")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "equity_curve.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = load_prices()
    log_a = np.log(prices["Price_A"])
    log_b = np.log(prices["Price_B"])

    eg = engle_granger_test(log_a, log_b)
    z = build_zscore(eg["residual_spread"])

    df = prices.copy()
    df["Position"] = generate_positions(z)
    df = run_backtest(df, eg["hedge_ratio"])

    num_trades = int((df["Position"].diff().fillna(0) != 0).sum())
    stats = performance_stats(df["StrategyReturn"], df["StrategyEquity"])

    df.round(4).to_csv(os.path.join(OUTPUT_DIR, "backtest_detail.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "pairs_trading_summary.txt"), "w") as f:
        f.write("=== Engle-Granger Cointegration Test ===\n")
        f.write(f"Hedge Ratio (OLS beta): {eg['hedge_ratio']:.4f}\n")
        f.write(f"ADF test on residual spread: statistic={eg['adf_stat']:.4f}, p-value={eg['adf_pvalue']:.6f}\n")
        f.write(f"  -> {'STATIONARY (cointegrated)' if eg['adf_pvalue'] < 0.05 else 'NOT stationary (no cointegration evidence)'}"
                f" at 5% significance\n")
        f.write(f"statsmodels coint() cross-check: statistic={eg['coint_stat']:.4f}, p-value={eg['coint_pvalue']:.6f}\n\n")
        f.write("=== Backtest Performance ===\n")
        f.write(f"Number of trades: {num_trades}\n")
        for k, v in stats.items():
            f.write(f"{k}: {v:.4f}\n")

    plot_prices_and_spread(df, eg["residual_spread"], z)
    plot_equity_curve(df)

    print("=== Pairs Trading / Cointegration ===")
    print(f"Hedge Ratio: {eg['hedge_ratio']:.4f}")
    print(f"ADF p-value on residual spread: {eg['adf_pvalue']:.6f}  "
          f"({'stationary -> cointegrated' if eg['adf_pvalue'] < 0.05 else 'not stationary'})")
    print(f"coint() cross-check p-value: {eg['coint_pvalue']:.6f}\n")
    print(f"Number of trades: {num_trades}")
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
