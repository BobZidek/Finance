"""
Mean-Variance Portfolio Optimizer - Efficient Frontier

Builds the Markowitz efficient frontier for an 8-asset universe: for a
range of target returns, finds the minimum-variance long-only portfolio
via constrained quadratic optimization (scipy.optimize.minimize), then
identifies the Global Minimum Variance portfolio and the Maximum Sharpe
Ratio (tangency) portfolio, and plots the Capital Market Line.

Run:
    python optimizer_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

RISK_FREE_RATE = 0.04


def load_assumptions():
    assets = pd.read_csv(os.path.join(DATA_DIR, "asset_assumptions.csv"))
    corr = pd.read_csv(os.path.join(DATA_DIR, "correlation_matrix.csv"), index_col="Asset")
    return assets, corr


def build_covariance(assets: pd.DataFrame, corr: pd.DataFrame) -> np.ndarray:
    vols = assets["Volatility"].values
    corr_matrix = corr.values

    # Defensive check: correlation matrices assembled by hand can end up not
    # positive semi-definite. Clip any negative eigenvalues to zero and
    # reconstruct, so the optimizer never sees an invalid covariance matrix.
    eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)
    if (eigenvalues < -1e-8).any():
        eigenvalues_clipped = np.clip(eigenvalues, 1e-8, None)
        corr_matrix = eigenvectors @ np.diag(eigenvalues_clipped) @ eigenvectors.T
        d = np.sqrt(np.diag(corr_matrix))
        corr_matrix = corr_matrix / np.outer(d, d)
        print("[optimizer] Correlation matrix was not PSD - corrected via eigenvalue clipping.")

    cov = np.outer(vols, vols) * corr_matrix
    return cov


def portfolio_stats(weights: np.ndarray, mean_returns: np.ndarray, cov: np.ndarray):
    port_return = weights @ mean_returns
    port_vol = np.sqrt(weights @ cov @ weights)
    return port_return, port_vol


def minimize_variance_for_target(mean_returns, cov, target_return, n_assets):
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        {"type": "eq", "fun": lambda w: w @ mean_returns - target_return},
    ]
    bounds = [(0.0, 1.0)] * n_assets
    x0 = np.repeat(1 / n_assets, n_assets)

    result = minimize(lambda w: w @ cov @ w, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    return result


def global_min_variance(mean_returns, cov, n_assets):
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0.0, 1.0)] * n_assets
    x0 = np.repeat(1 / n_assets, n_assets)
    result = minimize(lambda w: w @ cov @ w, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    return result


def max_sharpe(mean_returns, cov, n_assets, rf):
    def neg_sharpe(w):
        ret, vol = portfolio_stats(w, mean_returns, cov)
        return -(ret - rf) / vol

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0.0, 1.0)] * n_assets
    x0 = np.repeat(1 / n_assets, n_assets)
    result = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    return result


def build_efficient_frontier(mean_returns, cov, n_assets, n_points=40):
    min_ret, max_ret = mean_returns.min(), mean_returns.max()
    target_returns = np.linspace(min_ret, max_ret, n_points)

    rows = []
    for target in target_returns:
        result = minimize_variance_for_target(mean_returns, cov, target, n_assets)
        if result.success:
            vol = np.sqrt(result.x @ cov @ result.x)
            rows.append({"TargetReturn": target, "Volatility": vol, "Weights": result.x})
    return pd.DataFrame(rows)


def plot_frontier(frontier: pd.DataFrame, assets: pd.DataFrame, gmv, tangency, rf):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(frontier["Volatility"] * 100, frontier["TargetReturn"] * 100, color="#2E5090",
            linewidth=2, label="Efficient Frontier")

    ax.scatter(assets["Volatility"] * 100, assets["ExpectedReturn"] * 100, color="#7FA6D9", s=50,
               label="Individual Assets", zorder=4)
    for _, row in assets.iterrows():
        ax.annotate(row["Asset"], (row["Volatility"] * 100, row["ExpectedReturn"] * 100),
                    fontsize=7, xytext=(5, 3), textcoords="offset points")

    ax.scatter([gmv["vol"] * 100], [gmv["ret"] * 100], color="#1E8449", s=120, marker="*", zorder=5,
               label="Global Min Variance")
    ax.scatter([tangency["vol"] * 100], [tangency["ret"] * 100], color="#C0392B", s=120, marker="*", zorder=5,
               label="Max Sharpe (Tangency)")

    cml_x = np.linspace(0, tangency["vol"] * 1.4, 20)
    cml_y = rf + (tangency["ret"] - rf) / tangency["vol"] * cml_x
    ax.plot(cml_x * 100, cml_y * 100, linestyle="--", color="grey", label="Capital Market Line")

    ax.set_xlabel("Volatility (Annualized Std. Dev., %)")
    ax.set_ylabel("Expected Return (%)")
    ax.set_title("Efficient Frontier - 8 Asset Classes")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "efficient_frontier.png"), dpi=150)
    plt.close(fig)


def plot_weights(assets: pd.DataFrame, gmv_weights, tangency_weights):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(assets))
    width = 0.35
    ax.bar(x - width / 2, gmv_weights * 100, width, label="Global Min Variance", color="#1E8449")
    ax.bar(x + width / 2, tangency_weights * 100, width, label="Max Sharpe (Tangency)", color="#C0392B")
    ax.set_xticks(x)
    ax.set_xticklabels(assets["Asset"], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Portfolio Weight (%)")
    ax.set_title("Portfolio Weights: GMV vs. Tangency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "portfolio_weights.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    assets, corr = load_assumptions()
    cov = build_covariance(assets, corr)
    mean_returns = assets["ExpectedReturn"].values
    n_assets = len(assets)

    frontier = build_efficient_frontier(mean_returns, cov, n_assets)
    frontier_export = frontier[["TargetReturn", "Volatility"]].copy()
    frontier_export.round(4).to_csv(os.path.join(OUTPUT_DIR, "efficient_frontier.csv"), index=False)

    gmv_result = global_min_variance(mean_returns, cov, n_assets)
    gmv_ret, gmv_vol = portfolio_stats(gmv_result.x, mean_returns, cov)
    gmv = {"ret": gmv_ret, "vol": gmv_vol, "x": gmv_result.x}

    tangency_result = max_sharpe(mean_returns, cov, n_assets, RISK_FREE_RATE)
    tan_ret, tan_vol = portfolio_stats(tangency_result.x, mean_returns, cov)
    tangency = {"ret": tan_ret, "vol": tan_vol, "x": tangency_result.x}
    tangency_sharpe = (tan_ret - RISK_FREE_RATE) / tan_vol

    weights_df = pd.DataFrame({
        "Asset": assets["Asset"],
        "GMV_Weight": gmv_result.x,
        "Tangency_Weight": tangency_result.x,
    })
    weights_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "portfolio_weights.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "optimizer_summary.txt"), "w") as f:
        f.write("=== Global Minimum Variance Portfolio ===\n")
        f.write(f"Expected Return: {gmv_ret:.2%}  |  Volatility: {gmv_vol:.2%}  |  "
                f"Sharpe: {(gmv_ret - RISK_FREE_RATE) / gmv_vol:.2f}\n\n")
        f.write("=== Maximum Sharpe Ratio (Tangency) Portfolio ===\n")
        f.write(f"Expected Return: {tan_ret:.2%}  |  Volatility: {tan_vol:.2%}  |  "
                f"Sharpe: {tangency_sharpe:.2f}\n\n")
        f.write(weights_df.round(4).to_string(index=False))

    plot_frontier(frontier, assets, gmv, tangency, RISK_FREE_RATE)
    plot_weights(assets, gmv_result.x, tangency_result.x)

    print("=== Portfolio Optimizer: Efficient Frontier ===")
    print(f"\nGlobal Min Variance: Return {gmv_ret:.2%}  |  Vol {gmv_vol:.2%}  |  "
          f"Sharpe {(gmv_ret - RISK_FREE_RATE) / gmv_vol:.2f}")
    print(f"Max Sharpe (Tangency): Return {tan_ret:.2%}  |  Vol {tan_vol:.2%}  |  Sharpe {tangency_sharpe:.2f}")
    print("\n=== Portfolio Weights ===")
    print(weights_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
