"""
Black-Scholes Options Pricing Calculator with Greeks

Computes European call and put prices and their Greeks (Delta, Gamma,
Vega, Theta, Rho) via the closed-form Black-Scholes-Merton formula,
verifies put-call parity holds, and charts price/Greeks sensitivity
across a range of spot prices, plus a payoff diagram at expiration.

Run:
    python black_scholes_model.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_parameters() -> dict:
    path = os.path.join(DATA_DIR, "option_parameters.csv")
    df = pd.read_csv(path, index_col="Field")
    p = {k: v for k, v in df["Value"].items()}
    for k in p:
        if k != "UnderlyingName":
            p[k] = float(p[k])
    return p


def d1_d2(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_price(S, K, T, r, sigma, option_type="call"):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def bs_greeks(S, K, T, r, sigma, option_type="call") -> dict:
    d1, d2 = d1_d2(S, K, T, r, sigma)
    pdf_d1 = norm.pdf(d1)

    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T) / 100  # per 1% vol change

    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    return {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho}


def verify_put_call_parity(S, K, T, r, sigma) -> dict:
    call = bs_price(S, K, T, r, sigma, "call")
    put = bs_price(S, K, T, r, sigma, "put")
    lhs = call - put
    rhs = S - K * np.exp(-r * T)
    return {"call": call, "put": put, "lhs_C_minus_P": lhs, "rhs_S_minus_PV_K": rhs, "diff": lhs - rhs}


def plot_price_vs_spot(K, T, r, sigma):
    spots = np.linspace(50, 150, 100)
    call_prices = [bs_price(s, K, T, r, sigma, "call") for s in spots]
    put_prices = [bs_price(s, K, T, r, sigma, "put") for s in spots]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(spots, call_prices, label="Call Price", color="#2E5090")
    ax.plot(spots, put_prices, label="Put Price", color="#C0392B")
    ax.axvline(K, color="grey", linestyle="--", linewidth=1, label=f"Strike (${K:.0f})")
    ax.set_xlabel("Spot Price ($)")
    ax.set_ylabel("Option Price ($)")
    ax.set_title("Black-Scholes Option Price vs. Spot Price")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "price_vs_spot.png"), dpi=150)
    plt.close(fig)


def plot_greeks_vs_spot(K, T, r, sigma):
    spots = np.linspace(50, 150, 100)
    call_deltas = [bs_greeks(s, K, T, r, sigma, "call")["Delta"] for s in spots]
    put_deltas = [bs_greeks(s, K, T, r, sigma, "put")["Delta"] for s in spots]
    gammas = [bs_greeks(s, K, T, r, sigma, "call")["Gamma"] for s in spots]
    vegas = [bs_greeks(s, K, T, r, sigma, "call")["Vega"] for s in spots]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].plot(spots, call_deltas, label="Call Delta", color="#2E5090")
    axes[0].plot(spots, put_deltas, label="Put Delta", color="#C0392B")
    axes[0].axvline(K, color="grey", linestyle="--", linewidth=1)
    axes[0].set_title("Delta vs. Spot")
    axes[0].set_xlabel("Spot Price ($)")
    axes[0].legend(fontsize=8)

    axes[1].plot(spots, gammas, color="#1E8449")
    axes[1].axvline(K, color="grey", linestyle="--", linewidth=1)
    axes[1].set_title("Gamma vs. Spot (same for call & put)")
    axes[1].set_xlabel("Spot Price ($)")

    axes[2].plot(spots, vegas, color="#7FA6D9")
    axes[2].axvline(K, color="grey", linestyle="--", linewidth=1)
    axes[2].set_title("Vega vs. Spot (same for call & put)")
    axes[2].set_xlabel("Spot Price ($)")

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "greeks_vs_spot.png"), dpi=150)
    plt.close(fig)


def plot_payoff_diagram(S, K, T, r, sigma):
    call_price = bs_price(S, K, T, r, sigma, "call")
    put_price = bs_price(S, K, T, r, sigma, "put")

    spots_at_expiry = np.linspace(50, 150, 100)
    call_payoff = np.maximum(spots_at_expiry - K, 0) - call_price
    put_payoff = np.maximum(K - spots_at_expiry, 0) - put_price

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(spots_at_expiry, call_payoff, label="Long Call P&L at Expiry", color="#2E5090")
    ax.plot(spots_at_expiry, put_payoff, label="Long Put P&L at Expiry", color="#C0392B")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(K, color="grey", linestyle="--", linewidth=1, label=f"Strike (${K:.0f})")
    ax.set_xlabel("Spot Price at Expiry ($)")
    ax.set_ylabel("Profit / Loss ($)")
    ax.set_title("Payoff Diagram at Expiration (net of premium paid)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "payoff_diagram.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = load_parameters()
    S, K, T, r, sigma = p["SpotPrice"], p["StrikePrice"], p["TimeToExpiryYears"], p["RiskFreeRate"], p["Volatility"]

    call_price = bs_price(S, K, T, r, sigma, "call")
    put_price = bs_price(S, K, T, r, sigma, "put")
    call_greeks = bs_greeks(S, K, T, r, sigma, "call")
    put_greeks = bs_greeks(S, K, T, r, sigma, "put")
    parity = verify_put_call_parity(S, K, T, r, sigma)

    summary_df = pd.DataFrame([
        {"OptionType": "Call", "Price": call_price, **call_greeks},
        {"OptionType": "Put", "Price": put_price, **put_greeks},
    ])
    summary_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "pricing_and_greeks.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "black_scholes_summary.txt"), "w") as f:
        f.write(f"Underlying: {p['UnderlyingName']}\n")
        f.write(f"Spot: ${S:.2f}  |  Strike: ${K:.2f}  |  Time to Expiry: {T:.2f} years  |  "
                f"Risk-Free Rate: {r:.2%}  |  Volatility: {sigma:.2%}\n\n")
        f.write(summary_df.round(4).to_string(index=False))
        f.write("\n\n=== Put-Call Parity Check ===\n")
        f.write(f"C - P = {parity['lhs_C_minus_P']:.4f}\n")
        f.write(f"S - PV(K) = {parity['rhs_S_minus_PV_K']:.4f}\n")
        f.write(f"Difference: {parity['diff']:.10f} (should be ~0)\n")

    plot_price_vs_spot(K, T, r, sigma)
    plot_greeks_vs_spot(K, T, r, sigma)
    plot_payoff_diagram(S, K, T, r, sigma)

    print(f"=== Black-Scholes Pricing: {p['UnderlyingName']} ===")
    print(f"Spot ${S:.2f}  |  Strike ${K:.2f}  |  T={T:.2f}yr  |  r={r:.2%}  |  sigma={sigma:.2%}\n")
    print(summary_df.round(4).to_string(index=False))
    print(f"\nPut-Call Parity check: C-P = {parity['lhs_C_minus_P']:.4f}  vs.  "
          f"S-PV(K) = {parity['rhs_S_minus_PV_K']:.4f}  (diff: {parity['diff']:.2e})")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
