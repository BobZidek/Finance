"""
Fixed Income Duration, Convexity & Key Rate Duration

Prices a 4-bond portfolio off a hand-specified spot yield curve (linearly
interpolated between key maturities), computes Macaulay duration,
modified duration, and convexity for each bond, verifies the
duration+convexity price approximation against actual re-pricing at
shocked yields (demonstrating why convexity is needed for large yield
moves), and computes portfolio-level Key Rate Durations - sensitivity to
shifting each individual point on the yield curve while holding the
others fixed.

Run:
    python fixed_income_model.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_curve() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "yield_curve.csv")).sort_values("Maturity_Years").reset_index(drop=True)


def load_bonds() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "bond_portfolio.csv"))


def interpolate_rate(curve: pd.DataFrame, maturity: float) -> float:
    maturities = curve["Maturity_Years"].values
    rates = curve["SpotRate"].values
    if maturity <= maturities[0]:
        return rates[0]
    if maturity >= maturities[-1]:
        return rates[-1]
    return float(np.interp(maturity, maturities, rates))


def bond_cash_flows(maturity_years: float, coupon_rate: float, face_value: float):
    n_periods = int(round(maturity_years * 2))
    coupon = face_value * coupon_rate / 2
    times = [(i + 1) / 2 for i in range(n_periods)]
    cash_flows = [coupon] * n_periods
    cash_flows[-1] += face_value
    return times, cash_flows


def price_bond(times, cash_flows, yield_rate: float) -> float:
    return sum(cf / (1 + yield_rate / 2) ** (t * 2) for t, cf in zip(times, cash_flows))


def macaulay_duration(times, cash_flows, yield_rate: float, price: float) -> float:
    weighted_times = sum(t * cf / (1 + yield_rate / 2) ** (t * 2) for t, cf in zip(times, cash_flows))
    return weighted_times / price


def convexity(times, cash_flows, yield_rate: float, price: float) -> float:
    total = sum(cf * t * (t + 0.5) / (1 + yield_rate / 2) ** (t * 2) for t, cf in zip(times, cash_flows))
    return total / (price * (1 + yield_rate / 2) ** 2)


def analyze_bond(row, curve: pd.DataFrame) -> dict:
    ytm = interpolate_rate(curve, row["MaturityYears"])
    times, cash_flows = bond_cash_flows(row["MaturityYears"], row["CouponRate"], row["FaceValue"])
    price = price_bond(times, cash_flows, ytm)
    mac_dur = macaulay_duration(times, cash_flows, ytm, price)
    mod_dur = mac_dur / (1 + ytm / 2)
    conv = convexity(times, cash_flows, ytm, price)
    return {"Bond": row["Bond"], "MaturityYears": row["MaturityYears"], "YTM": ytm, "Price": price,
            "MacaulayDuration": mac_dur, "ModifiedDuration": mod_dur, "Convexity": conv,
            "_times": times, "_cash_flows": cash_flows}


def price_shock_validation(bond_analysis: dict, shocks_bps: list) -> pd.DataFrame:
    rows = []
    for shock_bps in shocks_bps:
        shock = shock_bps / 10000
        new_yield = bond_analysis["YTM"] + shock
        actual_price = price_bond(bond_analysis["_times"], bond_analysis["_cash_flows"], new_yield)
        actual_pct_change = actual_price / bond_analysis["Price"] - 1

        duration_only_est = -bond_analysis["ModifiedDuration"] * shock
        duration_convexity_est = duration_only_est + 0.5 * bond_analysis["Convexity"] * shock ** 2

        rows.append({"ShockBps": shock_bps, "ActualPctChange": actual_pct_change * 100,
                     "DurationOnlyEstimate": duration_only_est * 100,
                     "DurationConvexityEstimate": duration_convexity_est * 100,
                     "DurationOnlyError": (duration_only_est - actual_pct_change) * 100,
                     "DurationConvexityError": (duration_convexity_est - actual_pct_change) * 100})
    return pd.DataFrame(rows)


def key_rate_durations(bonds: pd.DataFrame, curve: pd.DataFrame, bump_bps: float = 1.0) -> pd.DataFrame:
    bump = bump_bps / 10000
    rows = []
    for _, row in bonds.iterrows():
        times, cash_flows = bond_cash_flows(row["MaturityYears"], row["CouponRate"], row["FaceValue"])
        base_ytm = interpolate_rate(curve, row["MaturityYears"])
        base_price = price_bond(times, cash_flows, base_ytm)

        krd_row = {"Bond": row["Bond"]}
        total_krd = 0.0
        for key_maturity in curve["Maturity_Years"]:
            bumped_curve = curve.copy()
            bumped_curve.loc[bumped_curve["Maturity_Years"] == key_maturity, "SpotRate"] += bump
            bumped_ytm = interpolate_rate(bumped_curve, row["MaturityYears"])
            bumped_price = price_bond(times, cash_flows, bumped_ytm)
            krd = -(bumped_price / base_price - 1) / bump
            krd_row[f"KRD_{int(key_maturity)}yr"] = krd
            total_krd += krd
        krd_row["TotalKRD"] = total_krd
        rows.append(krd_row)
    return pd.DataFrame(rows)


def plot_price_shock_accuracy(shock_df: pd.DataFrame, bond_name: str):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(shock_df["ShockBps"], shock_df["ActualPctChange"], marker="o", label="Actual (re-priced)",
            color="black", linewidth=2)
    ax.plot(shock_df["ShockBps"], shock_df["DurationOnlyEstimate"], marker="s", label="Duration-Only Estimate",
            color="#C0392B", linestyle="--")
    ax.plot(shock_df["ShockBps"], shock_df["DurationConvexityEstimate"], marker="^",
            label="Duration + Convexity Estimate", color="#1E8449", linestyle="--")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.set_xlabel("Yield Shock (bps)")
    ax.set_ylabel("Price Change (%)")
    ax.set_title(f"Price Sensitivity Approximation Accuracy - {bond_name}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "price_shock_accuracy.png"), dpi=150)
    plt.close(fig)


def plot_krd(krd_df: pd.DataFrame, key_maturities: list):
    fig, ax = plt.subplots(figsize=(9, 6))
    krd_cols = [f"KRD_{int(m)}yr" for m in key_maturities]
    bottom = pd.Series([0.0] * len(krd_df))
    colors = plt.cm.tab10.colors
    x = range(len(krd_df))
    width = 0.6
    for i, col in enumerate(krd_cols):
        ax.bar(x, krd_df[col], bottom=bottom, label=col, width=width, color=colors[i % len(colors)])
        bottom += krd_df[col]
    ax.set_xticks(list(x))
    ax.set_xticklabels(krd_df["Bond"], rotation=15, ha="right")
    ax.set_ylabel("Key Rate Duration")
    ax.set_title("Key Rate Duration by Bond (stacked, sums to Modified Duration)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "key_rate_durations.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    curve = load_curve()
    bonds = load_bonds()

    analyses = [analyze_bond(row, curve) for _, row in bonds.iterrows()]
    summary_df = pd.DataFrame([{k: v for k, v in a.items() if not k.startswith("_")} for a in analyses])

    total_mv = summary_df["Price"].sum()
    summary_df["Weight"] = summary_df["Price"] / total_mv
    portfolio_duration = (summary_df["Weight"] * summary_df["ModifiedDuration"]).sum()
    portfolio_convexity = (summary_df["Weight"] * summary_df["Convexity"]).sum()

    summary_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "bond_analysis.csv"), index=False)

    # Price shock validation on the longest-duration bond (where convexity matters most)
    longest_bond = max(analyses, key=lambda a: a["ModifiedDuration"])
    shocks = [-300, -200, -100, -50, 0, 50, 100, 200, 300]
    shock_df = price_shock_validation(longest_bond, shocks)
    shock_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "price_shock_validation.csv"), index=False)

    krd_df = key_rate_durations(bonds, curve)
    krd_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "key_rate_durations.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "fixed_income_summary.txt"), "w") as f:
        f.write("=== Bond Analysis ===\n")
        f.write(summary_df.round(4).to_string(index=False))
        f.write(f"\n\nPortfolio Modified Duration: {portfolio_duration:.3f}\n")
        f.write(f"Portfolio Convexity: {portfolio_convexity:.3f}\n\n")
        f.write(f"=== Price Shock Validation: {longest_bond['Bond']} "
                f"(Modified Duration {longest_bond['ModifiedDuration']:.2f}) ===\n")
        f.write(shock_df.round(4).to_string(index=False))
        f.write("\n\n=== Key Rate Durations ===\n")
        f.write(krd_df.round(4).to_string(index=False))

    plot_price_shock_accuracy(shock_df, longest_bond["Bond"])
    plot_krd(krd_df, curve["Maturity_Years"].tolist())

    print("=== Fixed Income Duration, Convexity & Key Rate Duration ===")
    print(summary_df.round(4).to_string(index=False))
    print(f"\nPortfolio Modified Duration: {portfolio_duration:.3f}  |  Portfolio Convexity: {portfolio_convexity:.3f}")
    print(f"\n=== Price Shock Validation: {longest_bond['Bond']} ===")
    print(shock_df.round(4).to_string(index=False))
    print("\n=== Key Rate Durations ===")
    print(krd_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
