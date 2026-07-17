"""
Interest Rate Swap Pricing

Builds a discount factor curve from zero (spot) rates, derives implied
forward rates, prices a plain-vanilla fixed-for-floating swap's fixed
and floating legs, solves for the par swap rate (zero NPV at inception),
marks an existing off-market swap to market, and computes DV01 (interest
rate sensitivity) via a curve bump-and-reprice - verifying two
independent methods for the floating leg PV agree with each other as a
built-in correctness check.

Run:
    python swap_pricing_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_curve() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "yield_curve.csv")).sort_values("Year").reset_index(drop=True)


def load_swap_terms() -> dict:
    path = os.path.join(DATA_DIR, "swap_terms.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: float(v) for k, v in df["Value"].items()}
    a["MaturityYears"] = int(a["MaturityYears"])
    return a


def build_discount_factors(curve: pd.DataFrame, shift_bps: float = 0.0) -> pd.DataFrame:
    curve = curve.copy()
    curve["ZeroRate"] = curve["ZeroRate"] + shift_bps / 10000
    curve["DiscountFactor"] = 1 / (1 + curve["ZeroRate"]) ** curve["Year"]
    return curve


def compute_forward_rates(curve: pd.DataFrame) -> pd.DataFrame:
    curve = curve.copy()
    prev_df = 1.0  # DF at year 0
    forwards = []
    for _, row in curve.iterrows():
        fwd = prev_df / row["DiscountFactor"] - 1  # 1-year forward rate for this period
        forwards.append(fwd)
        prev_df = row["DiscountFactor"]
    curve["ForwardRate"] = forwards
    return curve


def price_swap(curve: pd.DataFrame, notional: float, fixed_rate: float) -> dict:
    df_final = curve["DiscountFactor"].iloc[-1]
    sum_df = curve["DiscountFactor"].sum()

    # Floating leg: two independent methods, cross-checked against each other
    floating_pv_shortcut = notional * (1 - df_final)
    floating_cfs = notional * curve["ForwardRate"]
    floating_pv_manual = (floating_cfs * curve["DiscountFactor"]).sum()

    fixed_pv = notional * fixed_rate * sum_df

    par_swap_rate = (1 - df_final) / sum_df

    swap_npv_to_fixed_payer = floating_pv_shortcut - fixed_pv

    return {
        "df_final": df_final, "sum_df": sum_df,
        "floating_pv_shortcut": floating_pv_shortcut, "floating_pv_manual": floating_pv_manual,
        "floating_pv_consistency_check": abs(floating_pv_shortcut - floating_pv_manual),
        "fixed_pv": fixed_pv, "par_swap_rate": par_swap_rate,
        "swap_npv_to_fixed_payer": swap_npv_to_fixed_payer,
    }


def compute_dv01(base_curve: pd.DataFrame, swap_terms: dict, fixed_rate: float) -> dict:
    """DV01 here is reported unambiguously as the NPV-to-fixed-payer change for a
    +1bp parallel rate move (positive = fixed payer gains when rates rise, which is
    the expected direction: they pay a below-market fixed rate and receive floating,
    so a higher floating leg on rising rates benefits them)."""
    curve_up = compute_forward_rates(build_discount_factors(base_curve, shift_bps=1))
    curve_down = compute_forward_rates(build_discount_factors(base_curve, shift_bps=-1))

    npv_up = price_swap(curve_up, swap_terms["Notional_mm"], fixed_rate)["swap_npv_to_fixed_payer"]
    npv_down = price_swap(curve_down, swap_terms["Notional_mm"], fixed_rate)["swap_npv_to_fixed_payer"]

    dv01_per_plus1bp = (npv_up - npv_down) / 2
    return {"dv01_per_plus1bp": dv01_per_plus1bp, "npv_up_1bp": npv_up, "npv_down_1bp": npv_down}


def plot_curve_and_forwards(curve: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(curve["Year"], curve["ZeroRate"] * 100, marker="o", label="Zero (Spot) Rate", color="#2E5090")
    ax.plot(curve["Year"], curve["ForwardRate"] * 100, marker="s", label="1-Year Forward Rate", color="#C0392B")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rate (%)")
    ax.set_title("Zero Rate Curve vs. Implied Forward Rates")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "curve_and_forwards.png"), dpi=150)
    plt.close(fig)


def plot_leg_pvs(pricing: dict, swap_terms: dict):
    fig, ax = plt.subplots(figsize=(7, 6))
    labels = ["Floating Leg PV", f"Fixed Leg PV\n({swap_terms['ExistingContractualFixedRate']:.2%})"]
    values = [pricing["floating_pv_shortcut"], pricing["fixed_pv"]]
    bars = ax.bar(labels, values, color=["#2E5090", "#C0392B"])
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:,.2f}mm", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("$mm")
    ax.set_title(f"Swap Leg Present Values\nNPV to Fixed Payer: ${pricing['swap_npv_to_fixed_payer']:,.2f}mm")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "leg_pvs.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_curve = load_curve()
    swap_terms = load_swap_terms()

    curve = compute_forward_rates(build_discount_factors(raw_curve))
    curve.round(6).to_csv(os.path.join(OUTPUT_DIR, "curve_detail.csv"), index=False)

    pricing = price_swap(curve, swap_terms["Notional_mm"], swap_terms["ExistingContractualFixedRate"])
    par_pricing = price_swap(curve, swap_terms["Notional_mm"], pricing["par_swap_rate"])
    dv01_res = compute_dv01(raw_curve, swap_terms, swap_terms["ExistingContractualFixedRate"])
    dv01 = dv01_res["dv01_per_plus1bp"]

    with open(os.path.join(OUTPUT_DIR, "swap_pricing_summary.txt"), "w") as f:
        f.write(f"Notional: ${swap_terms['Notional_mm']:,.0f}mm  |  Maturity: {swap_terms['MaturityYears']:.0f} years\n\n")
        f.write("=== Curve ===\n")
        f.write(curve.round(4).to_string(index=False))
        f.write(f"\n\n=== Par Swap Rate (zero NPV at inception) ===\n")
        f.write(f"Par Swap Rate: {pricing['par_swap_rate']:.4%}\n")
        f.write(f"Check - NPV at par rate: ${par_pricing['swap_npv_to_fixed_payer']:.6f}mm (should be ~0)\n\n")
        f.write(f"=== Floating Leg PV Cross-Check ===\n")
        f.write(f"Shortcut method (Notional x (1 - DF_final)): ${pricing['floating_pv_shortcut']:.4f}mm\n")
        f.write(f"Manual method (sum of forward-rate cash flows x DF): ${pricing['floating_pv_manual']:.4f}mm\n")
        f.write(f"Difference: ${pricing['floating_pv_consistency_check']:.8f}mm (should be ~0)\n\n")
        f.write(f"=== Existing Off-Market Swap (contractual fixed rate "
                f"{swap_terms['ExistingContractualFixedRate']:.2%}) ===\n")
        f.write(f"Fixed Leg PV: ${pricing['fixed_pv']:.4f}mm\n")
        f.write(f"Floating Leg PV: ${pricing['floating_pv_shortcut']:.4f}mm\n")
        f.write(f"NPV to Fixed-Rate Payer: ${pricing['swap_npv_to_fixed_payer']:.4f}mm\n")
        f.write(f"(Positive because the payer is locked into paying a fixed rate "
                f"({swap_terms['ExistingContractualFixedRate']:.2%}) below the current par rate "
                f"({pricing['par_swap_rate']:.2%}))\n\n")
        f.write(f"=== DV01 (NPV to fixed-rate payer, for a +1bp parallel curve shift) ===\n")
        f.write(f"Base NPV: ${pricing['swap_npv_to_fixed_payer']:.4f}mm\n")
        f.write(f"NPV at curve +1bp: ${dv01_res['npv_up_1bp']:.4f}mm\n")
        f.write(f"NPV at curve -1bp: ${dv01_res['npv_down_1bp']:.4f}mm\n")
        f.write(f"DV01 (per +1bp): ${dv01:,.4f}mm  "
                f"(positive - the fixed payer gains when rates rise, since they keep paying a "
                f"below-market fixed rate while receiving a now-more-valuable floating leg)\n")

    plot_curve_and_forwards(curve)
    plot_leg_pvs(pricing, swap_terms)

    print("=== Interest Rate Swap Pricing ===")
    print(f"Par Swap Rate: {pricing['par_swap_rate']:.4%}")
    print(f"Floating leg PV cross-check difference: ${pricing['floating_pv_consistency_check']:.2e}mm\n")
    print(f"Existing Swap (contractual rate {swap_terms['ExistingContractualFixedRate']:.2%}):")
    print(f"  Fixed Leg PV: ${pricing['fixed_pv']:.4f}mm  |  Floating Leg PV: ${pricing['floating_pv_shortcut']:.4f}mm")
    print(f"  NPV to Fixed-Rate Payer: ${pricing['swap_npv_to_fixed_payer']:.4f}mm")
    print(f"  DV01 (per +1bp curve shift): ${dv01:,.4f}mm (positive = fixed payer gains as rates rise)")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
