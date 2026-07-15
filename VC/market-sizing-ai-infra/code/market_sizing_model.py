"""
Market Sizing (TAM/SAM/SOM) - Vector Database & AI Retrieval Infrastructure

Builds a top-down AND bottom-up TAM estimate for an emerging market
category, triangulates between them (since they will rarely match
exactly - the gap itself is informative), derives SAM and SOM, and
projects a 5-year market growth trajectory.

Run:
    python market_sizing_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "market_sizing_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "Sector":
            a[k] = float(a[k])
    a["BaseYear"] = int(a["BaseYear"])
    a["ProjectionYears"] = int(a["ProjectionYears"])
    return a


def load_competitive_landscape() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "competitive_landscape.csv"))


def top_down_tam(a: dict, year_offset: int) -> float:
    base_tam_bn = a["TopDown_GlobalEnterpriseSoftwareSpend_bn"] * a["TopDown_PctAttributableToAIInfra"]
    return base_tam_bn * (1 + a["TopDown_AnnualGrowthRate"]) ** year_offset


def bottom_up_tam(a: dict, year_offset: int) -> float:
    base_tam_bn = (a["BottomUp_TargetEnterpriseCount"] * a["BottomUp_AvgAnnualSpendPerEnterprise_thousands"]
                   * 1000) / 1e9
    return base_tam_bn * (1 + a["BottomUp_AnnualGrowthRate"]) ** year_offset


def build_projection(a: dict) -> pd.DataFrame:
    rows = []
    for year_offset in range(a["ProjectionYears"] + 1):
        td = top_down_tam(a, year_offset)
        bu = bottom_up_tam(a, year_offset)
        midpoint_tam = (td + bu) / 2
        sam = midpoint_tam * a["SAM_PctOfTAM"]
        rows.append({
            "Year": a["BaseYear"] + year_offset, "TopDownTAM_bn": td, "BottomUpTAM_bn": bu,
            "MidpointTAM_bn": midpoint_tam, "SAM_bn": sam,
        })
    df = pd.DataFrame(rows)
    df["SOM_bn"] = None
    df.loc[df.index[-1], "SOM_bn"] = df["SAM_bn"].iloc[-1] * a["SOM_PctOfSAM_Year5"]
    return df


def plot_tam_triangulation(df: pd.DataFrame, sector: str):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(df["Year"], df["TopDownTAM_bn"], marker="o", label="Top-Down TAM", color="#C0392B")
    ax.plot(df["Year"], df["BottomUpTAM_bn"], marker="o", label="Bottom-Up TAM", color="#2E5090")
    ax.plot(df["Year"], df["MidpointTAM_bn"], marker="o", linestyle="--", label="Midpoint TAM (triangulated)",
            color="#1E8449")
    ax.fill_between(df["Year"], df["TopDownTAM_bn"], df["BottomUpTAM_bn"], color="grey", alpha=0.15)
    ax.set_ylabel("$bn")
    ax.set_title(f"TAM Triangulation - {sector}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "tam_triangulation.png"), dpi=150)
    plt.close(fig)


def plot_tam_sam_som(df: pd.DataFrame, sector: str):
    fig, ax = plt.subplots(figsize=(7, 6))
    final_year = df.iloc[-1]
    labels = ["TAM\n(midpoint)", "SAM", "SOM"]
    values = [final_year["MidpointTAM_bn"], final_year["SAM_bn"], final_year["SOM_bn"]]
    bars = ax.bar(labels, values, color=["#7FA6D9", "#2E5090", "#1E8449"])
    for bar, val in zip(bars, values):
        ax.annotate(f"${val:,.1f}bn", (bar.get_x() + bar.get_width() / 2, val), ha="center", va="bottom")
    ax.set_ylabel("$bn")
    ax.set_title(f"TAM / SAM / SOM - {sector} (Year {int(final_year['Year'])})")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "tam_sam_som.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    landscape = load_competitive_landscape()

    df = build_projection(a)
    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "tam_sam_som_projection.csv"), index=False)
    landscape.to_csv(os.path.join(OUTPUT_DIR, "competitive_landscape.csv"), index=False)

    plot_tam_triangulation(df, a["Sector"])
    plot_tam_sam_som(df, a["Sector"])

    final_year = df.iloc[-1]
    with open(os.path.join(OUTPUT_DIR, "market_sizing_summary.txt"), "w") as f:
        f.write(f"Sector: {a['Sector']}\n\n")
        f.write(f"Base Year ({a['BaseYear']}) TAM:\n")
        f.write(f"  Top-Down:  ${df.iloc[0]['TopDownTAM_bn']:,.2f}bn\n")
        f.write(f"  Bottom-Up: ${df.iloc[0]['BottomUpTAM_bn']:,.2f}bn\n")
        f.write(f"  Midpoint:  ${df.iloc[0]['MidpointTAM_bn']:,.2f}bn\n\n")
        f.write(f"Year {int(final_year['Year'])} (Year {a['ProjectionYears']:.0f}) Projection:\n")
        f.write(f"  Top-Down TAM:  ${final_year['TopDownTAM_bn']:,.2f}bn\n")
        f.write(f"  Bottom-Up TAM: ${final_year['BottomUpTAM_bn']:,.2f}bn\n")
        f.write(f"  Midpoint TAM:  ${final_year['MidpointTAM_bn']:,.2f}bn\n")
        f.write(f"  SAM ({a['SAM_PctOfTAM']:.0%} of TAM): ${final_year['SAM_bn']:,.2f}bn\n")
        f.write(f"  SOM ({a['SOM_PctOfSAM_Year5']:.0%} of SAM): ${final_year['SOM_bn']:,.2f}bn "
                f"(=${final_year['SOM_bn']*1000:,.0f}mm)\n\n")
        f.write("=== Competitive Landscape ===\n")
        f.write(landscape.to_string(index=False))

    print(f"=== Market Sizing: {a['Sector']} ===")
    print(df.round(2).to_string(index=False))
    print(f"\nYear {int(final_year['Year'])} SAM: ${final_year['SAM_bn']:,.2f}bn  |  "
          f"SOM: ${final_year['SOM_bn']:,.2f}bn (${final_year['SOM_bn']*1000:,.0f}mm)")
    print(f"\n=== Competitive Landscape ===")
    print(landscape[["CompetitorCategory", "ThreatLevel"]].to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
