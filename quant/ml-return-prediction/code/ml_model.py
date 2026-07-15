"""
ML Return-Prediction Model with Realistic Transaction Costs

Engineers momentum, volatility, and mean-reversion features from a
synthetic price series, trains Ridge (linear) and Random Forest
(nonlinear) models on a time-ordered train/test split (no shuffling -
that would leak future information into training), and backtests a
simple sign-based trading strategy on each model's out-of-sample
predictions, including realistic per-trade transaction costs.

Run:
    python generate_data.py   (first, if data/synthetic_prices.csv doesn't exist)
    python ml_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

TRANSACTION_COST_BPS = 5  # 5 basis points per position change, one-way
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.04
TRAIN_FRACTION = 0.7


def load_prices() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "synthetic_prices.csv"), parse_dates=["Date"])


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Return_1d"] = df["Close"].pct_change()
    df["Momentum_5d"] = df["Close"].pct_change(5)
    df["Momentum_20d"] = df["Close"].pct_change(20)
    df["Volatility_20d"] = df["Return_1d"].rolling(20).std()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["MeanReversion_Zscore"] = (df["Close"] - df["SMA_20"]) / df["SMA_20"]

    # Target: NEXT day's return - features must only use information available today
    df["TargetNextReturn"] = df["Return_1d"].shift(-1)

    df = df.dropna().reset_index(drop=True)
    return df


def time_ordered_split(df: pd.DataFrame):
    split_idx = int(len(df) * TRAIN_FRACTION)
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


FEATURE_COLS = ["Momentum_5d", "Momentum_20d", "Volatility_20d", "MeanReversion_Zscore"]


def train_models(train_df: pd.DataFrame):
    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["TargetNextReturn"].values

    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train, y_train)

    rf = RandomForestRegressor(n_estimators=200, max_depth=4, min_samples_leaf=20, random_state=42)
    rf.fit(X_train, y_train)

    return ridge, rf


def evaluate_predictions(model, test_df: pd.DataFrame, label: str) -> dict:
    X_test = test_df[FEATURE_COLS].values
    y_test = test_df["TargetNextReturn"].values
    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)
    directional_accuracy = (np.sign(preds) == np.sign(y_test)).mean()
    ic = np.corrcoef(preds, y_test)[0, 1]

    return {"Model": label, "MSE": mse, "DirectionalAccuracy": directional_accuracy,
            "InformationCoefficient": ic, "Predictions": preds}


def backtest_strategy(test_df: pd.DataFrame, predictions: np.ndarray, label: str) -> pd.DataFrame:
    df = test_df.copy()
    df["Prediction"] = predictions
    df["Position"] = np.sign(df["Prediction"])  # long if predicted positive, short if negative

    df["PositionChange"] = df["Position"].diff().fillna(df["Position"].iloc[0]).abs()
    df["TransactionCost"] = df["PositionChange"] * (TRANSACTION_COST_BPS / 10000)

    df["GrossStrategyReturn"] = df["Position"] * df["TargetNextReturn"]
    df["NetStrategyReturn"] = df["GrossStrategyReturn"] - df["TransactionCost"]

    df["GrossEquity"] = (1 + df["GrossStrategyReturn"]).cumprod()
    df["NetEquity"] = (1 + df["NetStrategyReturn"]).cumprod()
    df["BuyHoldEquity"] = (1 + df["TargetNextReturn"]).cumprod()

    df["Model"] = label
    return df


def performance_stats(returns: pd.Series, equity: pd.Series) -> dict:
    ann_return = returns.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else float("nan")
    max_drawdown = (equity / equity.cummax() - 1).min()
    return {"TotalReturn": equity.iloc[-1] - 1, "AnnReturn": ann_return, "AnnVol": ann_vol,
            "Sharpe": sharpe, "MaxDrawdown": max_drawdown}


def plot_equity_curves(backtests: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"Ridge": "#2E5090", "Random Forest": "#C0392B"}
    for label, df in backtests.items():
        ax.plot(df["Date"], df["NetEquity"], label=f"{label} (net of costs)", color=colors[label])
    first_label = list(backtests.keys())[0]
    ax.plot(backtests[first_label]["Date"], backtests[first_label]["BuyHoldEquity"],
            label="Buy & Hold", color="grey", linestyle="--")
    ax.set_ylabel("Growth of $1 (out-of-sample test period)")
    ax.set_title("ML Strategy Equity Curves (Net of Transaction Costs) vs. Buy & Hold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "equity_curves.png"), dpi=150)
    plt.close(fig)


def plot_gross_vs_net(backtests: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    for label, df in backtests.items():
        ax.plot(df["Date"], df["GrossEquity"], label=f"{label} (gross, no costs)", linestyle="--")
        ax.plot(df["Date"], df["NetEquity"], label=f"{label} (net of costs)")
    ax.set_ylabel("Growth of $1")
    ax.set_title("Impact of Transaction Costs: Gross vs. Net Strategy Returns")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "gross_vs_net.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = load_prices()
    features = engineer_features(prices)
    train_df, test_df = time_ordered_split(features)

    ridge, rf = train_models(train_df)

    eval_ridge = evaluate_predictions(ridge, test_df, "Ridge")
    eval_rf = evaluate_predictions(rf, test_df, "Random Forest")

    eval_summary = pd.DataFrame([
        {k: v for k, v in eval_ridge.items() if k != "Predictions"},
        {k: v for k, v in eval_rf.items() if k != "Predictions"},
    ])
    eval_summary.round(4).to_csv(os.path.join(OUTPUT_DIR, "model_evaluation.csv"), index=False)

    backtests = {
        "Ridge": backtest_strategy(test_df, eval_ridge["Predictions"], "Ridge"),
        "Random Forest": backtest_strategy(test_df, eval_rf["Predictions"], "Random Forest"),
    }

    perf_rows = []
    for label, df in backtests.items():
        gross_stats = performance_stats(df["GrossStrategyReturn"], df["GrossEquity"])
        net_stats = performance_stats(df["NetStrategyReturn"], df["NetEquity"])
        perf_rows.append({"Model": label, "Type": "Gross (no costs)", **gross_stats})
        perf_rows.append({"Model": label, "Type": "Net (with costs)", **net_stats})
    buyhold_stats = performance_stats(backtests["Ridge"]["TargetNextReturn"], backtests["Ridge"]["BuyHoldEquity"])
    perf_rows.append({"Model": "Buy & Hold", "Type": "N/A", **buyhold_stats})

    perf_df = pd.DataFrame(perf_rows)
    perf_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "backtest_performance.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "ml_model_summary.txt"), "w") as f:
        f.write("=== Model Evaluation (Out-of-Sample Test Set) ===\n")
        f.write(eval_summary.round(4).to_string(index=False))
        f.write("\n\n=== Backtest Performance ===\n")
        f.write(perf_df.round(4).to_string(index=False))

    plot_equity_curves(backtests)
    plot_gross_vs_net(backtests)

    print("=== ML Return-Prediction Model ===")
    print(eval_summary.round(4).to_string(index=False))
    print("\n=== Backtest Performance ===")
    print(perf_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
