"""
VC Method Valuation - NovaCart (hypothetical SMB e-commerce checkout startup)

Values an early-stage startup using the VC Method: work backward from an
assumed exit value and a target return multiple to an implied post-money
valuation today. Computes both the naive version (ignoring future
dilution) and the correctly adjusted version (accounting for dilution
from anticipated future financing rounds before exit) - and shows how
much the naive version overstates achievable pre-money valuation.

Run:
    python vc_method_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "valuation_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "StartupName":
            a[k] = float(a[k])
    return a


def load_future_rounds() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "future_dilution_rounds.csv"))


def compute_retention_ratio(future_rounds: pd.DataFrame) -> float:
    retention = 1.0
    for _, r in future_rounds.iterrows():
        retention *= (1 - r["ExpectedDilutionPct"])
    return retention


def vc_method(exit_value: float, required_roi: float, investment: float, retention_ratio: float = 1.0):
    target_ownership_at_exit = (investment * required_roi) / exit_value
    required_ownership_today = target_ownership_at_exit / retention_ratio
    post_money = investment / required_ownership_today
    pre_money = post_money - investment
    return {
        "target_ownership_at_exit": target_ownership_at_exit,
        "required_ownership_today": required_ownership_today,
        "post_money": post_money, "pre_money": pre_money,
    }


def sensitivity_table(exit_values: list, required_rois: list, investment: float, retention_ratio: float) -> pd.DataFrame:
    table = pd.DataFrame(index=[f"{roi:.0f}x ROI" for roi in required_rois],
                          columns=[f"${ev:,.0f}mm exit" for ev in exit_values])
    for roi in required_rois:
        for ev in exit_values:
            res = vc_method(ev, roi, investment, retention_ratio)
            table.loc[f"{roi:.0f}x ROI", f"${ev:,.0f}mm exit"] = round(res["pre_money"], 2)
    return table


def plot_naive_vs_adjusted(naive: dict, adjusted: dict, startup_name: str):
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Pre-Money\n(naive)", "Pre-Money\n(dilution-adjusted)"]
    values = [naive["pre_money"], adjusted["pre_money"]]
    bars = ax.bar(labels, values, color=["#C0392B", "#2E5090"])
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:,.2f}mm", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("$mm")
    ax.set_title(f"Naive vs. Dilution-Adjusted Pre-Money Valuation\n{startup_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "naive_vs_adjusted.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Dilution-Adjusted Pre-Money Valuation ($mm) - Exit Value x Required ROI")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"${data[i, j]:.1f}mm", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Pre-Money Valuation ($mm)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    future_rounds = load_future_rounds()

    retention_ratio = compute_retention_ratio(future_rounds)
    naive = vc_method(a["ExitValue_mm"], a["RequiredROI"], a["InvestmentAmount_mm"], retention_ratio=1.0)
    adjusted = vc_method(a["ExitValue_mm"], a["RequiredROI"], a["InvestmentAmount_mm"], retention_ratio=retention_ratio)

    sens = sensitivity_table(
        exit_values=[300, 400, 500, 600, 750],
        required_rois=[10, 15, 20, 25, 30],
        investment=a["InvestmentAmount_mm"], retention_ratio=retention_ratio,
    )
    sens.to_csv(os.path.join(OUTPUT_DIR, "sensitivity_table.csv"))

    with open(os.path.join(OUTPUT_DIR, "valuation_summary.txt"), "w") as f:
        f.write(f"Startup: {a['StartupName']}\n\n")
        f.write(f"Assumed Exit Value: ${a['ExitValue_mm']:,.0f}mm in {a['YearsToExit']:.0f} years\n")
        f.write(f"Required ROI: {a['RequiredROI']:.0f}x\n")
        f.write(f"Investment: ${a['InvestmentAmount_mm']:,.1f}mm\n")
        f.write(f"Anticipated future dilution rounds: "
                f"{', '.join(f'{r.FutureRound} ({r.ExpectedDilutionPct:.0%})' for r in future_rounds.itertuples())}\n")
        f.write(f"Retention Ratio (this investor's share surviving future dilution): {retention_ratio:.1%}\n\n")
        f.write("=== Naive VC Method (ignores future dilution) ===\n")
        f.write(f"Required ownership: {naive['required_ownership_today']:.1%}\n")
        f.write(f"Post-money valuation: ${naive['post_money']:,.2f}mm\n")
        f.write(f"Pre-money valuation: ${naive['pre_money']:,.2f}mm\n\n")
        f.write("=== Dilution-Adjusted VC Method (correct) ===\n")
        f.write(f"Target ownership at exit: {adjusted['target_ownership_at_exit']:.1%}\n")
        f.write(f"Required ownership TODAY (post future dilution, needs to be higher): "
                f"{adjusted['required_ownership_today']:.1%}\n")
        f.write(f"Post-money valuation: ${adjusted['post_money']:,.2f}mm\n")
        f.write(f"Pre-money valuation: ${adjusted['pre_money']:,.2f}mm\n\n")
        f.write(f"Naive method overstates achievable pre-money valuation by "
                f"${naive['pre_money'] - adjusted['pre_money']:,.2f}mm "
                f"({(naive['pre_money']/adjusted['pre_money'] - 1):.1%})\n")

    plot_naive_vs_adjusted(naive, adjusted, a["StartupName"])
    plot_sensitivity_heatmap(sens)

    print(f"=== VC Method Valuation: {a['StartupName']} ===")
    print(f"Retention Ratio: {retention_ratio:.1%}\n")
    print(f"Naive Pre-Money: ${naive['pre_money']:,.2f}mm  (required ownership {naive['required_ownership_today']:.1%})")
    print(f"Adjusted Pre-Money: ${adjusted['pre_money']:,.2f}mm  "
          f"(required ownership {adjusted['required_ownership_today']:.1%})")
    print(f"\nOverstatement from ignoring future dilution: "
          f"${naive['pre_money'] - adjusted['pre_money']:,.2f}mm")
    print("\n=== Sensitivity: Pre-Money Valuation ($mm) - Exit Value x Required ROI ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
