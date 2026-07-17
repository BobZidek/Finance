"""
Monte Carlo Exotic Option Pricing - Asian & Barrier Options

Simulates many risk-neutral geometric Brownian motion price paths and
prices three option types: a vanilla European call (used as a
validation check against the closed-form Black-Scholes price from
quant/options-pricing-black-scholes), an arithmetic-average Asian call
(path-dependent, no closed-form solution), and an up-and-out barrier
call (path-dependent, knocked out if the price ever crosses the
barrier). Reports Monte Carlo standard errors and 95% confidence
intervals, and shows how they shrink as the number of simulated paths grows.

Run:
    python monte_carlo_options_model.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

np.random.seed(202)


def load_parameters() -> dict:
    path = os.path.join(DATA_DIR, "option_parameters.csv")
    df = pd.read_csv(path, index_col="Field")
    p = {k: v for k, v in df["Value"].items()}
    for k in p:
        if k != "UnderlyingName":
            p[k] = float(p[k])
    p["NumSimulatedPaths"] = int(p["NumSimulatedPaths"])
    p["NumTimeSteps"] = int(p["NumTimeSteps"])
    return p


def black_scholes_call(S, K, T, r, sigma) -> float:
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def simulate_paths(p: dict) -> np.ndarray:
    n_paths, n_steps = p["NumSimulatedPaths"], p["NumTimeSteps"]
    dt = p["TimeToExpiryYears"] / n_steps
    drift = (p["RiskFreeRate"] - 0.5 * p["Volatility"] ** 2) * dt
    vol_step = p["Volatility"] * np.sqrt(dt)

    z = np.random.normal(0, 1, (n_paths, n_steps))
    log_returns = drift + vol_step * z
    log_paths = np.cumsum(log_returns, axis=1)
    paths = p["SpotPrice"] * np.exp(log_paths)
    paths = np.hstack([np.full((n_paths, 1), p["SpotPrice"]), paths])  # prepend t=0
    return paths


def price_vanilla_mc(paths: np.ndarray, p: dict) -> dict:
    terminal = paths[:, -1]
    payoffs = np.maximum(terminal - p["StrikePrice"], 0)
    return discount_and_summarize(payoffs, p)


def price_asian_mc(paths: np.ndarray, p: dict) -> dict:
    avg_price = paths[:, 1:].mean(axis=1)  # arithmetic average over the path (excluding t=0)
    payoffs = np.maximum(avg_price - p["StrikePrice"], 0)
    return discount_and_summarize(payoffs, p)


def price_barrier_mc(paths: np.ndarray, p: dict) -> dict:
    terminal = paths[:, -1]
    knocked_out = (paths >= p["BarrierLevel"]).any(axis=1)
    payoffs = np.where(knocked_out, 0.0, np.maximum(terminal - p["StrikePrice"], 0))
    result = discount_and_summarize(payoffs, p)
    result["knockout_rate"] = knocked_out.mean()
    return result


def discount_and_summarize(payoffs: np.ndarray, p: dict) -> dict:
    discounted = payoffs * np.exp(-p["RiskFreeRate"] * p["TimeToExpiryYears"])
    price = discounted.mean()
    std_error = discounted.std(ddof=1) / np.sqrt(len(discounted))
    ci_lower, ci_upper = price - 1.96 * std_error, price + 1.96 * std_error
    return {"price": price, "std_error": std_error, "ci_lower": ci_lower, "ci_upper": ci_upper}


def convergence_analysis(p: dict) -> pd.DataFrame:
    path_counts = [500, 1000, 2500, 5000, 10000, 25000, 50000]
    rows = []
    for n in path_counts:
        p_sub = dict(p)
        p_sub["NumSimulatedPaths"] = n
        paths = simulate_paths(p_sub)
        vanilla = price_vanilla_mc(paths, p_sub)
        rows.append({"NumPaths": n, "VanillaPrice": vanilla["price"], "StdError": vanilla["std_error"]})
    return pd.DataFrame(rows)


def plot_price_comparison(bs_price: float, vanilla: dict, asian: dict, barrier: dict, p: dict):
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = ["Black-Scholes\n(closed-form)", "Vanilla Call\n(Monte Carlo)", "Asian Call\n(avg. price)",
              "Up-and-Out\nBarrier Call"]
    prices = [bs_price, vanilla["price"], asian["price"], barrier["price"]]
    errors = [0, vanilla["std_error"] * 1.96, asian["std_error"] * 1.96, barrier["std_error"] * 1.96]
    colors = ["#7FA6D9", "#2E5090", "#1E8449", "#C0392B"]
    ax.bar(labels, prices, yerr=errors, capsize=5, color=colors)
    for i, price in enumerate(prices):
        ax.annotate(f"${price:.3f}", (i, price), ha="center", va="bottom")
    ax.set_ylabel("Option Price ($)")
    ax.set_title(f"Option Price Comparison - {p['UnderlyingName']}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "price_comparison.png"), dpi=150)
    plt.close(fig)


def plot_convergence(conv_df: pd.DataFrame, bs_price: float):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(conv_df["NumPaths"], conv_df["VanillaPrice"], marker="o", color="#2E5090", label="MC Estimate")
    ax.fill_between(conv_df["NumPaths"], conv_df["VanillaPrice"] - 1.96 * conv_df["StdError"],
                     conv_df["VanillaPrice"] + 1.96 * conv_df["StdError"], color="#7FA6D9", alpha=0.3,
                     label="95% CI")
    ax.axhline(bs_price, color="#C0392B", linestyle="--", label=f"Black-Scholes (${bs_price:.4f})")
    ax.set_xscale("log")
    ax.set_xlabel("Number of Simulated Paths (log scale)")
    ax.set_ylabel("Vanilla Call Price ($)")
    ax.set_title("Monte Carlo Convergence to the Closed-Form Black-Scholes Price")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "convergence.png"), dpi=150)
    plt.close(fig)


def plot_sample_paths(paths: np.ndarray, p: dict, n_show: int = 60):
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(n_show):
        ax.plot(paths[i], alpha=0.3, linewidth=0.7)
    ax.axhline(p["StrikePrice"], color="black", linestyle="--", linewidth=1, label=f"Strike (${p['StrikePrice']:.0f})")
    ax.axhline(p["BarrierLevel"], color="#C0392B", linestyle="--", linewidth=1, label=f"Barrier (${p['BarrierLevel']:.0f})")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Price")
    ax.set_title("Sample Simulated Price Paths")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sample_paths.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = load_parameters()

    bs_price = black_scholes_call(p["SpotPrice"], p["StrikePrice"], p["TimeToExpiryYears"],
                                    p["RiskFreeRate"], p["Volatility"])

    paths = simulate_paths(p)
    vanilla = price_vanilla_mc(paths, p)
    asian = price_asian_mc(paths, p)
    barrier = price_barrier_mc(paths, p)

    conv_df = convergence_analysis(p)
    conv_df.round(6).to_csv(os.path.join(OUTPUT_DIR, "convergence_analysis.csv"), index=False)

    mc_vs_bs_diff = vanilla["price"] - bs_price
    within_ci = vanilla["ci_lower"] <= bs_price <= vanilla["ci_upper"]

    with open(os.path.join(OUTPUT_DIR, "exotic_options_summary.txt"), "w") as f:
        f.write(f"Underlying: {p['UnderlyingName']}\n")
        f.write(f"Spot: ${p['SpotPrice']:.2f}  |  Strike: ${p['StrikePrice']:.2f}  |  T={p['TimeToExpiryYears']:.2f}yr  |  "
                f"r={p['RiskFreeRate']:.2%}  |  sigma={p['Volatility']:.2%}\n")
        f.write(f"Barrier Level: ${p['BarrierLevel']:.2f}  |  Simulated Paths: {p['NumSimulatedPaths']:,}\n\n")
        f.write("=== Validation: Vanilla Call, Monte Carlo vs. Closed-Form Black-Scholes ===\n")
        f.write(f"Black-Scholes (closed-form): ${bs_price:.4f}\n")
        f.write(f"Monte Carlo estimate: ${vanilla['price']:.4f}  (95% CI: ${vanilla['ci_lower']:.4f} - "
                f"${vanilla['ci_upper']:.4f})\n")
        f.write(f"Difference: ${mc_vs_bs_diff:+.4f}  |  Black-Scholes price falls within the MC 95% CI: "
                f"{within_ci}\n\n")
        f.write("=== Asian (Arithmetic Average) Call ===\n")
        f.write(f"Price: ${asian['price']:.4f}  (95% CI: ${asian['ci_lower']:.4f} - ${asian['ci_upper']:.4f})\n")
        f.write(f"Discount vs. vanilla: {1 - asian['price']/vanilla['price']:.1%} "
                f"(averaging reduces effective volatility of the payoff)\n\n")
        f.write("=== Up-and-Out Barrier Call ===\n")
        f.write(f"Price: ${barrier['price']:.4f}  (95% CI: ${barrier['ci_lower']:.4f} - ${barrier['ci_upper']:.4f})\n")
        f.write(f"Knock-out rate (probability barrier is breached before expiry): {barrier['knockout_rate']:.1%}\n")
        f.write(f"Discount vs. vanilla: {1 - barrier['price']/vanilla['price']:.1%} "
                f"(knock-out risk reduces value)\n\n")
        f.write("=== Convergence Analysis ===\n")
        f.write(conv_df.round(6).to_string(index=False))

    plot_price_comparison(bs_price, vanilla, asian, barrier, p)
    plot_convergence(conv_df, bs_price)
    plot_sample_paths(paths, p)

    print(f"=== Monte Carlo Exotic Option Pricing: {p['UnderlyingName']} ===")
    print(f"Black-Scholes (closed-form): ${bs_price:.4f}")
    print(f"Vanilla (Monte Carlo): ${vanilla['price']:.4f}  (95% CI: ${vanilla['ci_lower']:.4f} - "
          f"${vanilla['ci_upper']:.4f})  |  BS within CI: {within_ci}")
    print(f"Asian Call: ${asian['price']:.4f}  ({1 - asian['price']/vanilla['price']:.1%} discount to vanilla)")
    print(f"Barrier Call: ${barrier['price']:.4f}  ({1 - barrier['price']/vanilla['price']:.1%} discount to vanilla, "
          f"{barrier['knockout_rate']:.1%} knockout rate)")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
