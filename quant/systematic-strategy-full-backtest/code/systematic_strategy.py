"""
Full Systematic Strategy Backtest - Signal, Portfolio Construction,
Risk Management, and Performance Attribution

Extends the single-snapshot multi-factor ranking approach (see
quant/multi-factor-stock-ranking) into a genuine multi-period systematic
strategy: monthly signal generation (Value/Momentum/Quality composite),
dollar-neutral long/short quintile portfolio construction, volatility
targeting (risk management), turnover-based transaction costs, and a
full backtest with regression-based performance attribution back to the
three underlying factors.

Run:
    python generate_data.py   (first, if data/factor_panel.csv doesn't exist)
    python systematic_strategy.py
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

TARGET_ANNUAL_VOL = 0.08
VOL_LOOKBACK_MONTHS = 6
MAX_LEVERAGE_SCALAR = 2.0
TRANSACTION_COST_BPS = 15  # per unit of one-way turnover
RISK_FREE_RATE = 0.04
MONTHS_PER_YEAR = 12


def load_panel() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "factor_panel.csv"), parse_dates=["Date"])


def long_short_return(group: pd.DataFrame, score_col: str) -> tuple:
    """Equal-weighted top-quintile-minus-bottom-quintile return for one month,
    given a factor/composite score column. Returns (return, weights_series)."""
    group = group.copy()
    group["Quintile"] = pd.qcut(group[score_col], 5, labels=False, duplicates="drop")
    n_q = group["Quintile"].nunique()
    top_q, bottom_q = n_q - 1, 0

    top = group[group["Quintile"] == top_q]
    bottom = group[group["Quintile"] == bottom_q]

    weights = pd.Series(0.0, index=group["Ticker"])
    weights.loc[top["Ticker"]] = 1 / len(top)
    weights.loc[bottom["Ticker"]] = -1 / len(bottom)

    ret = (weights.values * group.set_index("Ticker").loc[weights.index, "ForwardReturn_1m"].values).sum()
    return ret, weights


def build_monthly_signal_returns(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel["CompositeZ"] = (panel["ValueZ"] + panel["MomentumZ"] + panel["QualityZ"]) / 3

    rows = []
    weight_history = {}
    for date, group in panel.groupby("Date"):
        composite_ret, composite_w = long_short_return(group, "CompositeZ")
        value_ret, _ = long_short_return(group, "ValueZ")
        momentum_ret, _ = long_short_return(group, "MomentumZ")
        quality_ret, _ = long_short_return(group, "QualityZ")

        rows.append({"Date": date, "CompositeRawReturn": composite_ret, "ValueFactorReturn": value_ret,
                     "MomentumFactorReturn": momentum_ret, "QualityFactorReturn": quality_ret})
        weight_history[date] = composite_w

    signal_df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    return signal_df, weight_history


def apply_risk_management(signal_df: pd.DataFrame, weight_history: dict) -> pd.DataFrame:
    df = signal_df.copy()
    monthly_target_vol = TARGET_ANNUAL_VOL / np.sqrt(MONTHS_PER_YEAR)

    scalars, turnovers = [], []
    dates = df["Date"].tolist()
    prev_weights = None

    for i, date in enumerate(dates):
        trailing = df["CompositeRawReturn"].iloc[max(0, i - VOL_LOOKBACK_MONTHS):i]
        if len(trailing) < 3:
            scalar = 1.0
        else:
            trailing_vol = trailing.std()
            scalar = monthly_target_vol / trailing_vol if trailing_vol > 0 else 1.0
            scalar = min(scalar, MAX_LEVERAGE_SCALAR)
        scalars.append(scalar)

        current_weights = weight_history[date] * scalar
        if prev_weights is None:
            turnover = current_weights.abs().sum() / 2
        else:
            turnover = (current_weights - prev_weights).abs().sum() / 2
        turnovers.append(turnover)
        prev_weights = current_weights

    df["VolScalar"] = scalars
    df["Turnover"] = turnovers
    df["ScaledReturn"] = df["CompositeRawReturn"] * df["VolScalar"]
    df["TransactionCost"] = df["Turnover"] * (TRANSACTION_COST_BPS / 10000)
    df["NetReturn"] = df["ScaledReturn"] - df["TransactionCost"]
    df["NetEquity"] = (1 + df["NetReturn"]).cumprod()
    df["GrossEquity"] = (1 + df["ScaledReturn"]).cumprod()
    return df


def performance_stats(returns: pd.Series, equity: pd.Series) -> dict:
    ann_return = returns.mean() * MONTHS_PER_YEAR
    ann_vol = returns.std() * np.sqrt(MONTHS_PER_YEAR)
    sharpe = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else float("nan")
    max_drawdown = (equity / equity.cummax() - 1).min()
    return {"TotalReturn": equity.iloc[-1] - 1, "AnnReturn": ann_return, "AnnVol": ann_vol,
            "Sharpe": sharpe, "MaxDrawdown": max_drawdown}


def performance_attribution(df: pd.DataFrame) -> dict:
    X = sm.add_constant(df[["ValueFactorReturn", "MomentumFactorReturn", "QualityFactorReturn"]])
    y = df["NetReturn"]
    model = sm.OLS(y, X).fit()

    contributions = {}
    for factor in ["ValueFactorReturn", "MomentumFactorReturn", "QualityFactorReturn"]:
        beta = model.params[factor]
        contributions[factor] = beta * df[factor].sum()

    return {"model": model, "contributions": contributions}


def plot_equity_curve(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Date"], df["NetEquity"], label="Net of Costs", color="#2E5090")
    ax.plot(df["Date"], df["GrossEquity"], label="Gross (vol-targeted, no costs)", color="#7FA6D9", linestyle="--")
    ax.axhline(1.0, color="grey", linestyle=":", linewidth=1)
    ax.set_ylabel("Growth of $1")
    ax.set_title("Systematic Strategy Equity Curve (Vol-Targeted Long/Short)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "equity_curve.png"), dpi=150)
    plt.close(fig)


def plot_attribution(contributions: dict):
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = [k.replace("FactorReturn", "") for k in contributions]
    values = [v * 100 for v in contributions.values()]
    ax.bar(labels, values, color=["#2E5090", "#C0392B", "#1E8449"])
    ax.set_ylabel("Cumulative Return Contribution (%)")
    ax.set_title("Performance Attribution by Factor")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "performance_attribution.png"), dpi=150)
    plt.close(fig)


def plot_vol_targeting(df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["Date"], df["CompositeRawReturn"] * 100, width=20, color="#7FA6D9", label="Raw Return (%)")
    ax2.plot(df["Date"], df["VolScalar"], color="#C0392B", label="Vol Scalar")
    ax1.set_ylabel("Raw Monthly Return (%)")
    ax2.set_ylabel("Volatility Targeting Scalar")
    ax1.set_title("Raw Signal Return vs. Volatility-Targeting Scalar")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "vol_targeting.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    panel = load_panel()

    signal_df, weight_history = build_monthly_signal_returns(panel)
    df = apply_risk_management(signal_df, weight_history)
    df.round(4).to_csv(os.path.join(OUTPUT_DIR, "monthly_backtest_detail.csv"), index=False)

    net_stats = performance_stats(df["NetReturn"], df["NetEquity"])
    gross_stats = performance_stats(df["ScaledReturn"], df["GrossEquity"])
    unscaled_stats = performance_stats(df["CompositeRawReturn"], (1 + df["CompositeRawReturn"]).cumprod())

    stats_df = pd.DataFrame([
        {"Version": "Net of Costs (vol-targeted)", **net_stats},
        {"Version": "Gross (vol-targeted, no costs)", **gross_stats},
        {"Version": "Unscaled Raw Signal", **unscaled_stats},
    ])
    stats_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "performance_summary.csv"), index=False)

    attribution = performance_attribution(df)
    attribution_df = pd.DataFrame([
        {"Factor": k.replace("FactorReturn", ""), "Beta": attribution["model"].params[k],
         "PValue": attribution["model"].pvalues[k], "CumulativeContribution": attribution["contributions"][k]}
        for k in attribution["contributions"]
    ])
    attribution_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "performance_attribution.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "strategy_summary.txt"), "w") as f:
        f.write("=== Systematic Strategy Backtest Summary ===\n\n")
        f.write(stats_df.round(4).to_string(index=False))
        f.write(f"\n\nTotal turnover-based transaction costs over backtest: "
                f"{df['TransactionCost'].sum():.2%}\n\n")
        f.write("=== Performance Attribution (regression of net returns on factor returns) ===\n")
        f.write(f"R-squared: {attribution['model'].rsquared:.3f}\n\n")
        f.write(attribution_df.round(4).to_string(index=False))

    plot_equity_curve(df)
    plot_attribution(attribution["contributions"])
    plot_vol_targeting(df)

    print("=== Systematic Strategy Backtest ===")
    print(stats_df.round(4).to_string(index=False))
    print(f"\nTotal transaction costs: {df['TransactionCost'].sum():.2%}")
    print(f"\n=== Performance Attribution (R^2 = {attribution['model'].rsquared:.3f}) ===")
    print(attribution_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
