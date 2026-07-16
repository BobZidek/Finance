"""
GARCH(1,1) Volatility Forecasting

Fits a GARCH(1,1) model to a synthetic return series that genuinely
exhibits volatility clustering, recovers the underlying (alpha, beta,
omega) parameters, compares GARCH's fitted conditional volatility
against a naive constant-volatility (unconditional standard deviation)
assumption and against a simple rolling-window volatility estimate, and
produces a forward volatility forecast.

Run:
    python generate_data.py   (first, if data/returns_with_true_vol.csv doesn't exist)
    python garch_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from arch import arch_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

ROLLING_WINDOW = 20
FORECAST_HORIZON_DAYS = 20
TRADING_DAYS_PER_YEAR = 252


def load_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "returns_with_true_vol.csv"), parse_dates=["Date"])


def fit_garch(returns: pd.Series):
    # arch_model expects returns scaled up (e.g. in %) for numerical stability
    scaled_returns = returns * 100
    model = arch_model(scaled_returns, vol="Garch", p=1, q=1, dist="normal", mean="Zero")
    fitted = model.fit(disp="off")
    return fitted


def compare_volatility_estimates(df: pd.DataFrame, fitted) -> pd.DataFrame:
    df = df.copy()
    df["RollingVol"] = df["Return"].rolling(ROLLING_WINDOW).std()
    df["ConstantVol"] = df["Return"].std()
    df["GARCH_ConditionalVol"] = fitted.conditional_volatility / 100  # undo the 100x scaling
    return df


def evaluate_forecast_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    """Compares each method's volatility estimate at time t against the
    REALIZED |return| the next day - a simple, standard way to check
    whether a volatility estimate actually tracks subsequent realized risk."""
    df = df.copy()
    df["NextDayAbsReturn"] = df["Return"].shift(-1).abs()
    df = df.dropna()

    rows = []
    for method in ["ConstantVol", "RollingVol", "GARCH_ConditionalVol"]:
        # Mean absolute error between the vol estimate and next-day realized |return|
        # (a proxy for realized volatility at the daily level)
        mae = (df[method] - df["NextDayAbsReturn"]).abs().mean()
        correlation = df[method].corr(df["NextDayAbsReturn"])
        rows.append({"Method": method, "MAE_vs_NextDayAbsReturn": mae,
                     "Correlation_vs_NextDayAbsReturn": correlation})
    return pd.DataFrame(rows)


def forecast_forward_volatility(fitted) -> pd.DataFrame:
    forecast = fitted.forecast(horizon=FORECAST_HORIZON_DAYS, reindex=False)
    variance_forecast = forecast.variance.values[-1] / (100 ** 2)  # undo scaling, back to variance units
    daily_vol_forecast = np.sqrt(variance_forecast)
    annualized_vol_forecast = daily_vol_forecast * np.sqrt(TRADING_DAYS_PER_YEAR)
    return pd.DataFrame({"HorizonDay": range(1, FORECAST_HORIZON_DAYS + 1),
                          "DailyVolForecast": daily_vol_forecast,
                          "AnnualizedVolForecast": annualized_vol_forecast})


def plot_volatility_comparison(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["Date"], df["TrueVolatility"], label="True Volatility (from data-generating process)",
            color="black", linewidth=1, alpha=0.6)
    ax.plot(df["Date"], df["GARCH_ConditionalVol"], label="GARCH(1,1) Fitted Conditional Vol",
            color="#2E5090", linewidth=1.2)
    ax.plot(df["Date"], df["RollingVol"], label=f"{ROLLING_WINDOW}-Day Rolling Vol",
            color="#C0392B", linewidth=1, alpha=0.7)
    ax.axhline(df["ConstantVol"].iloc[0], color="grey", linestyle="--", label="Constant (Unconditional) Vol")
    ax.set_ylabel("Daily Volatility")
    ax.set_title("Volatility Estimates: True vs. GARCH vs. Rolling vs. Constant")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "volatility_comparison.png"), dpi=150)
    plt.close(fig)


def plot_forecast(forecast_df: pd.DataFrame, current_annualized_vol: float):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(forecast_df["HorizonDay"], forecast_df["AnnualizedVolForecast"] * 100, marker="o", color="#2E5090")
    ax.axhline(current_annualized_vol * 100, color="grey", linestyle="--",
               label="Long-Run Unconditional Annualized Vol")
    ax.set_xlabel("Trading Days Ahead")
    ax.set_ylabel("Forecasted Annualized Volatility (%)")
    ax.set_title(f"GARCH(1,1) {FORECAST_HORIZON_DAYS}-Day Forward Volatility Forecast")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "volatility_forecast.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw = load_data()

    fitted = fit_garch(raw["Return"])
    df = compare_volatility_estimates(raw, fitted)
    accuracy = evaluate_forecast_accuracy(df)
    accuracy.round(6).to_csv(os.path.join(OUTPUT_DIR, "forecast_accuracy_comparison.csv"), index=False)

    forecast_df = forecast_forward_volatility(fitted)
    forecast_df.round(6).to_csv(os.path.join(OUTPUT_DIR, "volatility_forecast.csv"), index=False)

    long_run_var = fitted.params["omega"] / (100 ** 2) / (1 - fitted.params["alpha[1]"] - fitted.params["beta[1]"])
    long_run_annualized_vol = np.sqrt(long_run_var * TRADING_DAYS_PER_YEAR)

    df[["Date", "Return", "TrueVolatility", "ConstantVol", "RollingVol", "GARCH_ConditionalVol"]].round(6).to_csv(
        os.path.join(OUTPUT_DIR, "volatility_estimates_detail.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "garch_summary.txt"), "w") as f:
        f.write("=== GARCH(1,1) Fitted Parameters ===\n")
        f.write(f"omega: {fitted.params['omega'] / (100**2):.8f}\n")
        f.write(f"alpha[1]: {fitted.params['alpha[1]']:.4f}  (true value used to generate data: 0.09)\n")
        f.write(f"beta[1]: {fitted.params['beta[1]']:.4f}  (true value used to generate data: 0.88)\n")
        f.write(f"Persistence (alpha+beta): {fitted.params['alpha[1]'] + fitted.params['beta[1]']:.4f}  "
                f"(true value: 0.97)\n")
        f.write(f"Long-run unconditional annualized volatility: {long_run_annualized_vol:.2%}\n\n")
        f.write("=== Volatility Estimate Accuracy (vs. next-day realized |return|) ===\n")
        f.write(accuracy.round(6).to_string(index=False))
        f.write(f"\n\n=== {FORECAST_HORIZON_DAYS}-Day Forward Volatility Forecast ===\n")
        f.write(forecast_df.round(4).to_string(index=False))

    plot_volatility_comparison(df)
    plot_forecast(forecast_df, long_run_annualized_vol)

    print("=== GARCH(1,1) Volatility Forecasting ===")
    print(f"Fitted alpha={fitted.params['alpha[1]']:.4f} (true: 0.09), "
          f"beta={fitted.params['beta[1]']:.4f} (true: 0.88)")
    print(f"Persistence: {fitted.params['alpha[1]'] + fitted.params['beta[1]']:.4f} (true: 0.97)\n")
    print("=== Volatility Estimate Accuracy ===")
    print(accuracy.round(6).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
