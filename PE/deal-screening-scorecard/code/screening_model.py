"""
Deal Screening Scorecard - Multi-Sector Target Universe

Ranks a universe of 10 hypothetical acquisition targets across sectors on
a weighted composite score (growth, margin, leverage/debt capacity, free
cash flow conversion, customer concentration risk), using standardized
(z-score) metrics so factors on very different scales can be combined
into one ranking - the quantitative first pass of PE deal sourcing before
qualitative diligence begins.

Run:
    python screening_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_universe() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "target_universe.csv"))


def load_weights() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "scoring_weights.csv"))


def compute_scores(universe: pd.DataFrame, weights: pd.DataFrame):
    df = universe.copy()
    contribution_cols = []

    for _, w in weights.iterrows():
        metric = w["Metric"]
        weight = w["Weight"]
        higher_is_better = bool(w["HigherIsBetter"])

        mean = df[metric].mean()
        std = df[metric].std()
        z = (df[metric] - mean) / std
        if not higher_is_better:
            z = -z

        contrib_col = f"{metric}_WeightedZ"
        df[contrib_col] = z * weight
        contribution_cols.append(contrib_col)

    df["CompositeScore"] = df[contribution_cols].sum(axis=1)
    df["Rank"] = df["CompositeScore"].rank(ascending=False).astype(int)
    df = df.sort_values("CompositeScore", ascending=False).reset_index(drop=True)

    return df, contribution_cols


def plot_ranking(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    ordered = df.sort_values("CompositeScore")
    colors = ["#1E8449" if s > 0 else "#C0392B" for s in ordered["CompositeScore"]]
    ax.barh(ordered["Company"], ordered["CompositeScore"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Composite Score (weighted, standardized)")
    ax.set_title("Deal Screening Scorecard - Ranked Target Universe")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "ranking.png"), dpi=150)
    plt.close(fig)


def plot_score_breakdown(df: pd.DataFrame, contribution_cols: list):
    fig, ax = plt.subplots(figsize=(10, 6))
    ordered = df.sort_values("CompositeScore")
    bottom = pd.Series([0.0] * len(ordered), index=ordered.index)

    colors = plt.cm.tab10.colors
    for i, col in enumerate(contribution_cols):
        vals = ordered[col]
        ax.barh(ordered["Company"], vals, left=bottom, label=col.replace("_WeightedZ", ""),
                 color=colors[i % len(colors)])
        bottom += vals

    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Weighted Contribution to Composite Score")
    ax.set_title("Composite Score Breakdown by Factor")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "score_breakdown.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    universe = load_universe()
    weights = load_weights()

    scored, contribution_cols = compute_scores(universe, weights)

    display_cols = ["Rank", "Company", "Sector", "RevenueGrowth_3yrCAGR", "EBITDAMargin",
                     "NetDebt_EBITDA", "FCFConversion", "CustomerConcentration_pct", "CompositeScore"]
    scored[display_cols].round(3).to_csv(os.path.join(OUTPUT_DIR, "ranked_scorecard.csv"), index=False)

    plot_ranking(scored)
    plot_score_breakdown(scored, contribution_cols)

    top3 = scored.head(3)["Company"].tolist()
    with open(os.path.join(OUTPUT_DIR, "shortlist_summary.txt"), "w") as f:
        f.write("=== Deal Screening Scorecard: Ranked Target Universe ===\n\n")
        f.write(scored[display_cols].round(3).to_string(index=False))
        f.write(f"\n\nTop 3 shortlist for further diligence: {', '.join(top3)}\n")

    print("=== Deal Screening Scorecard ===")
    print(scored[display_cols].round(3).to_string(index=False))
    print(f"\nTop 3 shortlist: {', '.join(top3)}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
