"""
Optimal Execution & Market Impact - Almgren-Chriss Model

Solves for the optimal trading trajectory to liquidate a large equity
position over a fixed horizon, trading off market impact cost (which
favors trading slowly, to minimize price impact) against timing/
volatility risk (which favors trading quickly, to minimize exposure to
adverse price moves while the position sits unexecuted) - the classic
Almgren-Chriss (2000) framework. Compares the optimal trajectory against
naive TWAP (equal amounts each period) and immediate-liquidation
benchmarks, and builds an efficient frontier of execution strategies
across risk-aversion levels.

Run:
    python optimal_execution_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_parameters() -> dict:
    path = os.path.join(DATA_DIR, "execution_parameters.csv")
    df = pd.read_csv(path, index_col="Field")
    p = {k: v for k, v in df["Value"].items()}
    for k in p:
        if k != "AssetName":
            p[k] = float(p[k])
    p["NumPeriods"] = int(p["NumPeriods"])
    return p


def dollar_volatility(p: dict) -> float:
    return p["VolatilityPerPeriod"] * p["StockPrice"]


def almgren_chriss_trajectory(X: float, N: int, sigma: float, eta: float, gamma: float,
                                risk_aversion: float) -> np.ndarray:
    """Closed-form optimal remaining-position trajectory (continuous-time
    kappa approximation, standard and adequate for a normalized single-period
    tau=1 discretization)."""
    eta_tilde = eta - 0.5 * gamma
    if eta_tilde <= 0:
        eta_tilde = eta  # fallback guard against a degenerate parameter combination
    kappa = np.sqrt(risk_aversion * sigma ** 2 / eta_tilde)

    j = np.arange(0, N + 1)
    if kappa * N < 1e-6:
        # risk_aversion -> 0 limit: optimal trajectory converges to linear (TWAP)
        x_j = X * (1 - j / N)
    else:
        x_j = X * np.sinh(kappa * (N - j)) / np.sinh(kappa * N)
    return x_j


def twap_trajectory(X: float, N: int) -> np.ndarray:
    j = np.arange(0, N + 1)
    return X * (1 - j / N)


def immediate_trajectory(X: float, N: int) -> np.ndarray:
    x_j = np.zeros(N + 1)
    x_j[0] = X
    return x_j


def expected_cost_and_variance(x_j: np.ndarray, sigma: float, eta: float, gamma: float, X: float):
    v = -np.diff(x_j)  # shares traded each period
    eta_tilde = eta - 0.5 * gamma

    expected_cost = 0.5 * gamma * X ** 2 + eta_tilde * np.sum(v ** 2)
    cost_variance = sigma ** 2 * np.sum(x_j[1:] ** 2)  # holding-period risk from unexecuted shares
    return expected_cost, cost_variance, v


def build_comparison(p: dict) -> pd.DataFrame:
    X, N = p["SharesToLiquidate"], p["NumPeriods"]
    sigma = dollar_volatility(p)
    eta, gamma = p["TemporaryImpactCoefficient"], p["PermanentImpactCoefficient"]

    strategies = {
        "Almgren-Chriss Optimal": almgren_chriss_trajectory(X, N, sigma, eta, gamma, p["BaseRiskAversion"]),
        "TWAP (naive linear)": twap_trajectory(X, N),
        "Immediate Liquidation": immediate_trajectory(X, N),
    }

    rows = []
    trajectories = {}
    for name, x_j in strategies.items():
        cost, variance, v = expected_cost_and_variance(x_j, sigma, eta, gamma, X)
        notional = X * p["StockPrice"]
        rows.append({"Strategy": name, "ExpectedCost_dollars": cost, "CostStdDev_dollars": np.sqrt(variance),
                     "ExpectedCost_bps_of_notional": cost / notional * 10000,
                     "CostStdDev_bps_of_notional": np.sqrt(variance) / notional * 10000})
        trajectories[name] = x_j

    return pd.DataFrame(rows), trajectories


def efficient_frontier(p: dict) -> pd.DataFrame:
    X, N = p["SharesToLiquidate"], p["NumPeriods"]
    sigma = dollar_volatility(p)
    eta, gamma = p["TemporaryImpactCoefficient"], p["PermanentImpactCoefficient"]

    risk_aversions = np.logspace(-8, -3, 25)
    rows = []
    for lam in risk_aversions:
        x_j = almgren_chriss_trajectory(X, N, sigma, eta, gamma, lam)
        cost, variance, _ = expected_cost_and_variance(x_j, sigma, eta, gamma, X)
        rows.append({"RiskAversion": lam, "ExpectedCost_dollars": cost, "CostStdDev_dollars": np.sqrt(variance)})
    return pd.DataFrame(rows)


def plot_trajectories(trajectories: dict, N: int):
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {"Almgren-Chriss Optimal": "#2E5090", "TWAP (naive linear)": "#7FA6D9",
              "Immediate Liquidation": "#C0392B"}
    for name, x_j in trajectories.items():
        ax.plot(range(N + 1), x_j, marker="o", label=name, color=colors[name])
    ax.set_xlabel("Trading Period")
    ax.set_ylabel("Shares Remaining")
    ax.set_title("Execution Trajectories: Shares Remaining Over Time")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "execution_trajectories.png"), dpi=150)
    plt.close(fig)


def plot_efficient_frontier(frontier: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(frontier["CostStdDev_dollars"], frontier["ExpectedCost_dollars"], marker="o", color="#2E5090")
    ax.set_xlabel("Cost Standard Deviation ($) - Timing Risk")
    ax.set_ylabel("Expected Cost ($) - Market Impact")
    ax.set_title("Execution Efficient Frontier: Impact Cost vs. Timing Risk")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "efficient_frontier.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = load_parameters()

    comparison, trajectories = build_comparison(p)
    comparison.round(2).to_csv(os.path.join(OUTPUT_DIR, "strategy_comparison.csv"), index=False)

    frontier = efficient_frontier(p)
    frontier.round(2).to_csv(os.path.join(OUTPUT_DIR, "efficient_frontier.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "execution_summary.txt"), "w") as f:
        f.write(f"Asset: {p['AssetName']}\n")
        f.write(f"Shares to Liquidate: {p['SharesToLiquidate']:,.0f}  |  Notional: "
                f"${p['SharesToLiquidate'] * p['StockPrice']:,.0f}\n")
        f.write(f"Trading Periods: {p['NumPeriods']:.0f}  |  Per-Period Volatility: "
                f"{p['VolatilityPerPeriod']:.2%}\n\n")
        f.write("=== Strategy Comparison ===\n")
        f.write(comparison.round(2).to_string(index=False))
        f.write("\n\nNote: the Almgren-Chriss optimal strategy balances market impact cost (favoring slow "
                "trading) against timing risk (favoring fast trading) - it should show a lower cost standard "
                "deviation than TWAP for the same or lower expected cost, and both should show materially "
                "lower expected cost than immediate liquidation.\n")

    plot_trajectories(trajectories, p["NumPeriods"])
    plot_efficient_frontier(frontier)

    print(f"=== Optimal Execution: {p['AssetName']} ===")
    print(f"Liquidating {p['SharesToLiquidate']:,.0f} shares "
          f"(${p['SharesToLiquidate'] * p['StockPrice']:,.0f} notional) over {p['NumPeriods']:.0f} periods\n")
    print(comparison.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
