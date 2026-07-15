"""
Cap Table & Dilution Tracker - Seed (SAFEs) through Series C

Tracks a startup's fully-diluted cap table across a SAFE-funded seed stage
and three priced rounds (Series A, B, C), correctly modeling: SAFE
conversion (cap vs. discount, whichever is more favorable to the
investor) via a small iterative solver, and the option pool "top-up"
mechanic where a new pool is sized as a % of the POST-money cap table but
dilutes only PRE-money holders (primarily founders) - the single most
common source of confusion in real cap table math.

Run:
    python cap_table_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_founders_and_pool() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "founders_and_pool.csv"))


def load_safes() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "safes.csv"))


def load_priced_rounds() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "priced_rounds.csv"))


def solve_pool_topup(s_old: float, pre_money: float, post_money: float, target_pool_pct: float):
    """Solves the pool-shuffle algebra: pre-money fully-diluted shares (PMFD)
    such that the new pool shares added (PMFD - s_old) equal target_pool_pct
    of the POST-money fully diluted share count.

    Derivation: PostFD = PMFD * PostMoney / PreMoney, and
    (PMFD - s_old) / PostFD = target_pool_pct  =>  solved algebraically below.
    """
    pmfd = (s_old * pre_money) / (pre_money - target_pool_pct * post_money)
    new_pool_shares = pmfd - s_old
    price_per_share = pre_money / pmfd
    return pmfd, new_pool_shares, price_per_share


def process_seed_and_series_a(founders_pool: pd.DataFrame, safes: pd.DataFrame, series_a: pd.Series):
    """Iteratively resolves SAFE conversion (cap vs. discount) simultaneously
    with the Series A pool top-up and pricing, since a SAFE's discount price
    depends on the very Series A price its own conversion helps determine."""
    s_pre_safe = founders_pool["Shares"].sum()
    pre_money = series_a["PreMoneyValuation"]
    investment = series_a["Investment"]
    post_money = pre_money + investment
    target_pool_pct = series_a["TargetPoolPct"]

    safe_shares = {row["SAFEName"]: 0.0 for _, row in safes.iterrows()}

    for _ in range(50):
        s_old = s_pre_safe + sum(safe_shares.values())
        pmfd, new_pool_shares, price_per_share = solve_pool_topup(s_old, pre_money, post_money, target_pool_pct)

        new_safe_shares = {}
        for _, row in safes.iterrows():
            cap_price = row["ValuationCap"] / s_pre_safe
            discount_price = price_per_share * (1 - row["Discount"]) if row["Discount"] > 0 else float("inf")
            conversion_price = min(cap_price, discount_price)
            new_safe_shares[row["SAFEName"]] = row["InvestmentAmount"] / conversion_price

        if all(abs(new_safe_shares[k] - safe_shares[k]) < 1 for k in safe_shares):
            safe_shares = new_safe_shares
            break
        safe_shares = new_safe_shares

    s_old_final = s_pre_safe + sum(safe_shares.values())
    pmfd, new_pool_shares, price_per_share = solve_pool_topup(s_old_final, pre_money, post_money, target_pool_pct)
    new_investor_shares = investment / price_per_share

    return {
        "safe_shares": safe_shares, "new_pool_shares": new_pool_shares,
        "price_per_share": price_per_share, "new_investor_shares": new_investor_shares,
        "post_money_fd_shares": pmfd + new_investor_shares,
    }


def process_priced_round(s_old: float, round_row: pd.Series):
    pre_money = round_row["PreMoneyValuation"]
    investment = round_row["Investment"]
    target_pool_pct = round_row["TargetPoolPct"]

    if pd.isna(target_pool_pct):
        pmfd = s_old
        new_pool_shares = 0.0
        price_per_share = pre_money / pmfd
    else:
        post_money = pre_money + investment
        pmfd, new_pool_shares, price_per_share = solve_pool_topup(s_old, pre_money, post_money, target_pool_pct)

    new_investor_shares = investment / price_per_share
    return {"new_pool_shares": new_pool_shares, "price_per_share": price_per_share,
            "new_investor_shares": new_investor_shares, "post_money_fd_shares": pmfd + new_investor_shares}


def build_cap_table_history(founders_pool: pd.DataFrame, safes: pd.DataFrame, rounds: pd.DataFrame):
    holders = {}
    for _, r in founders_pool.iterrows():
        holders[r["Holder"]] = {"class": r["HolderClass"], "shares": r["Shares"]}

    history = []

    def snapshot(round_name, price_per_share):
        total = sum(h["shares"] for h in holders.values())
        by_class = {}
        for h in holders.values():
            by_class[h["class"]] = by_class.get(h["class"], 0) + h["shares"]
        row = {"Round": round_name, "PricePerShare": price_per_share, "TotalFDShares": total}
        for cls, shares in by_class.items():
            row[f"{cls}_Shares"] = shares
            row[f"{cls}_OwnershipPct"] = shares / total
        history.append(row)

    snapshot("Founding", None)

    series_a = rounds[rounds["RoundName"] == "Series A"].iloc[0]
    res_a = process_seed_and_series_a(founders_pool, safes, series_a)

    holders["Option Pool (unallocated)"]["shares"] += res_a["new_pool_shares"]
    for safe_name, shares in res_a["safe_shares"].items():
        holders[safe_name] = {"class": "Seed (SAFE)", "shares": shares}
    holders["Series A Investors"] = {"class": "Series A", "shares": res_a["new_investor_shares"]}

    snapshot("Series A", res_a["price_per_share"])

    for round_name in ["Series B", "Series C"]:
        round_row = rounds[rounds["RoundName"] == round_name].iloc[0]
        s_old = sum(h["shares"] for h in holders.values())
        res = process_priced_round(s_old, round_row)

        if res["new_pool_shares"] > 0:
            holders["Option Pool (unallocated)"]["shares"] += res["new_pool_shares"]
        holders[f"{round_name} Investors"] = {"class": round_name, "shares": res["new_investor_shares"]}

        snapshot(round_name, res["price_per_share"])

    return pd.DataFrame(history), holders


def plot_founder_dilution(history: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(history["Round"], history["Founders_OwnershipPct"] * 100, marker="o", color="#2E5090", linewidth=2)
    for x, y in zip(history["Round"], history["Founders_OwnershipPct"] * 100):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")
    ax.set_ylabel("Founder Ownership (%)")
    ax.set_title("Founder Ownership Dilution Across Rounds")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "founder_dilution.png"), dpi=150)
    plt.close(fig)


def plot_cap_table_stacked(history: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    pct_cols = [c for c in history.columns if c.endswith("_OwnershipPct")]
    bottom = pd.Series([0.0] * len(history))
    colors = plt.cm.tab10.colors
    for i, col in enumerate(pct_cols):
        vals = history[col].fillna(0) * 100
        ax.bar(history["Round"], vals, bottom=bottom, label=col.replace("_OwnershipPct", ""),
               color=colors[i % len(colors)])
        bottom += vals
    ax.set_ylabel("Ownership (%)")
    ax.set_title("Fully-Diluted Ownership by Round")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "cap_table_stacked.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    founders_pool = load_founders_and_pool()
    safes = load_safes()
    rounds = load_priced_rounds()

    history, holders = build_cap_table_history(founders_pool, safes, rounds)
    history.round(4).to_csv(os.path.join(OUTPUT_DIR, "cap_table_history.csv"), index=False)

    final_table = pd.DataFrame([{"Holder": name, "Class": h["class"], "Shares": h["shares"]}
                                 for name, h in holders.items()])
    final_table["OwnershipPct"] = final_table["Shares"] / final_table["Shares"].sum()
    final_table = final_table.sort_values("Shares", ascending=False)
    final_table.round(4).to_csv(os.path.join(OUTPUT_DIR, "final_cap_table.csv"), index=False)

    plot_founder_dilution(history)
    plot_cap_table_stacked(history)

    display_cols = ["Round", "PricePerShare", "TotalFDShares"] + \
        [c for c in history.columns if c.endswith("_OwnershipPct")]

    print("=== Cap Table History (Ownership % by Round) ===")
    print(history[display_cols].round(4).to_string(index=False))
    print("\n=== Final Cap Table (post-Series C) ===")
    print(final_table.round(4).to_string(index=False))
    print(f"\nFounder ownership: {history['Founders_OwnershipPct'].iloc[0]*100:.1f}% at founding -> "
          f"{history['Founders_OwnershipPct'].iloc[-1]*100:.1f}% post-Series C")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
