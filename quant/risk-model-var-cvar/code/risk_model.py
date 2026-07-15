"""
Portfolio Risk Model - VaR / CVaR via Historical, Parametric, and Monte Carlo Methods

Estimates 1-day Value-at-Risk and Conditional VaR (Expected Shortfall) for
a 5-asset portfolio three ways: (1) historical simulation on the actual
realized return sample, (2) parametric (variance-covariance), which
assumes normally distributed returns, and (3) Monte Carlo simulation
using a correctly-specified fat-tailed (Student-t) asset return model -
deliberately contrasting (2) and (3) to show how the normal-distribution
assumption understates tail risk when real returns are fat-tailed, which
the underlying data (generated via a Student-t distribution) genuinely is.

Run:
    python generate_data.py   (first, if data/asset_returns.csv doesn't exist)
    python risk_model.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import norm, t as student_t
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

CONFIDENCE_LEVELS = [0.95, 0.99]
MC_SIMULATIONS = 50000
MC_DEGREES_OF_FREEDOM = 4
PORTFOLIO_VALUE = 10_000_000  # $10mm illustrative portfolio


def load_data():
    returns = pd.read_csv(os.path.join(DATA_DIR, "asset_returns.csv"), parse_dates=["Date"])
    weights = pd.read_csv(os.path.join(DATA_DIR, "portfolio_weights.csv"))
    return returns, weights


def compute_portfolio_returns(returns: pd.DataFrame, weights: pd.DataFrame) -> pd.Series:
    w = weights.set_index("Asset")["Weight"]
    asset_cols = [c for c in returns.columns if c != "Date"]
    return returns[asset_cols].dot(w[asset_cols])


def historical_var_cvar(port_returns: pd.Series, confidence: float):
    alpha = 1 - confidence
    var = -np.percentile(port_returns, alpha * 100)
    tail_losses = port_returns[port_returns <= -var]
    cvar = -tail_losses.mean() if len(tail_losses) > 0 else var
    return var, cvar


def parametric_var_cvar(port_returns: pd.Series, confidence: float):
    mu, sigma = port_returns.mean(), port_returns.std()
    alpha = 1 - confidence
    z = norm.ppf(alpha)
    var = -(mu + z * sigma)
    cvar = -(mu - sigma * norm.pdf(z) / alpha)
    return var, cvar


def simulate_multivariate_t(n_rows: int, correlation: np.ndarray, df: float) -> np.ndarray:
    """Correct construction of a multivariate Student-t: X = Z_correlated / sqrt(W/df),
    where Z_correlated ~ N(0, correlation) and W ~ Chi-square(df) is drawn once per row
    and shared across all columns in that row - this produces genuine fat tails while
    preserving the target correlation structure between assets."""
    n_assets = correlation.shape[0]
    L = np.linalg.cholesky(correlation)
    z = np.random.normal(0, 1, (n_rows, n_assets)) @ L.T
    w = np.random.chisquare(df, size=(n_rows, 1))
    return z / np.sqrt(w / df)


def monte_carlo_var_cvar(returns: pd.DataFrame, weights: pd.DataFrame, confidence: float):
    asset_cols = [c for c in returns.columns if c != "Date"]
    mu = returns[asset_cols].mean().values
    corr = returns[asset_cols].corr().values
    vol = returns[asset_cols].std().values

    t_correlated = simulate_multivariate_t(MC_SIMULATIONS, corr, MC_DEGREES_OF_FREEDOM)
    t_correlated = t_correlated / np.sqrt(MC_DEGREES_OF_FREEDOM / (MC_DEGREES_OF_FREEDOM - 2))

    simulated_asset_returns = mu + t_correlated * vol
    w = weights.set_index("Asset")["Weight"][asset_cols].values
    simulated_port_returns = simulated_asset_returns @ w

    alpha = 1 - confidence
    var = -np.percentile(simulated_port_returns, alpha * 100)
    tail_losses = simulated_port_returns[simulated_port_returns <= -var]
    cvar = -tail_losses.mean() if len(tail_losses) > 0 else var
    return var, cvar, simulated_port_returns


def backtest_var(port_returns: pd.Series, var: float, confidence: float) -> dict:
    exceedances = (port_returns < -var).sum()
    expected_exceedances = len(port_returns) * (1 - confidence)
    return {"Exceedances": int(exceedances), "ExpectedExceedances": expected_exceedances,
            "ExceedanceRate": exceedances / len(port_returns)}


def plot_return_distribution(port_returns: pd.Series, mc_returns: np.ndarray, var_hist_95, var_param_95):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(port_returns * 100, bins=60, density=True, alpha=0.5, color="#7FA6D9", label="Historical (actual)")
    ax.hist(mc_returns * 100, bins=60, density=True, alpha=0.4, color="#1E8449",
            label="Monte Carlo (Student-t)", histtype="step", linewidth=1.5)

    mu, sigma = port_returns.mean(), port_returns.std()
    x = np.linspace(port_returns.min(), port_returns.max(), 200)
    ax.plot(x * 100, norm.pdf(x, mu, sigma) / 100, color="#C0392B", linewidth=2,
            label="Parametric Normal Fit")

    ax.axvline(-var_hist_95 * 100, color="#7FA6D9", linestyle="--", label="Historical 95% VaR")
    ax.axvline(-var_param_95 * 100, color="#C0392B", linestyle="--", label="Parametric 95% VaR")

    ax.set_xlabel("Daily Portfolio Return (%)")
    ax.set_ylabel("Density")
    ax.set_title("Portfolio Return Distribution: Historical vs. Monte Carlo (t) vs. Parametric Normal")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "return_distribution.png"), dpi=150)
    plt.close(fig)


def plot_method_comparison(results_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(results_df["ConfidenceLevel"].unique()))
    width = 0.25
    methods = results_df["Method"].unique()
    for i, method in enumerate(methods):
        subset = results_df[results_df["Method"] == method].sort_values("ConfidenceLevel")
        ax.bar(x + (i - 1) * width, subset["VaR_pct"] * 100, width, label=f"{method} VaR")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(c*100)}%" for c in sorted(results_df["ConfidenceLevel"].unique())])
    ax.set_xlabel("Confidence Level")
    ax.set_ylabel("1-Day VaR (% of portfolio)")
    ax.set_title("VaR by Method and Confidence Level")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "method_comparison.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    returns, weights = load_data()
    port_returns = compute_portfolio_returns(returns, weights)

    rows = []
    mc_returns_95 = None
    var_hist_95 = var_param_95 = None

    for confidence in CONFIDENCE_LEVELS:
        h_var, h_cvar = historical_var_cvar(port_returns, confidence)
        p_var, p_cvar = parametric_var_cvar(port_returns, confidence)
        mc_var, mc_cvar, mc_returns = monte_carlo_var_cvar(returns, weights, confidence)

        if confidence == 0.95:
            mc_returns_95 = mc_returns
            var_hist_95, var_param_95 = h_var, p_var

        for method, var, cvar in [("Historical", h_var, h_cvar), ("Parametric (Normal)", p_var, p_cvar),
                                    ("Monte Carlo (Student-t)", mc_var, mc_cvar)]:
            backtest = backtest_var(port_returns, var, confidence)
            rows.append({"ConfidenceLevel": confidence, "Method": method, "VaR_pct": var, "CVaR_pct": cvar,
                        "VaR_dollar": var * PORTFOLIO_VALUE, "CVaR_dollar": cvar * PORTFOLIO_VALUE,
                        **backtest})

    results_df = pd.DataFrame(rows)
    results_df.round(6).to_csv(os.path.join(OUTPUT_DIR, "var_cvar_comparison.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "risk_model_summary.txt"), "w") as f:
        f.write(f"Portfolio Value: ${PORTFOLIO_VALUE:,.0f}\n")
        f.write(f"Sample size: {len(port_returns)} trading days\n\n")
        f.write(results_df.round(4).to_string(index=False))
        f.write("\n\n=== Key Finding ===\n")
        gap = results_df[(results_df["Method"] == "Historical") & (results_df["ConfidenceLevel"] == 0.99)]["VaR_dollar"].values[0] - \
              results_df[(results_df["Method"] == "Parametric (Normal)") & (results_df["ConfidenceLevel"] == 0.99)]["VaR_dollar"].values[0]
        f.write(f"At 99% confidence, Historical VaR exceeds Parametric (Normal) VaR by ${gap:,.0f} - "
                f"the normal distribution assumption understates tail risk for this fat-tailed portfolio.\n")

    plot_return_distribution(port_returns, mc_returns_95, var_hist_95, var_param_95)
    plot_method_comparison(results_df)

    print("=== VaR / CVaR Risk Model ===")
    print(f"Portfolio Value: ${PORTFOLIO_VALUE:,.0f}\n")
    print(results_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
