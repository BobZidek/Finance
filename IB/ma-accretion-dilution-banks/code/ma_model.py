"""
M&A Accretion / Dilution Model - Regional Banks

Models a hypothetical stock + cash acquisition between two fictional regional
banks: computes purchase price, consideration mix, pro forma combined EPS,
and whether the deal is accretive or dilutive to the acquirer's standalone
EPS. Also produces a Cash% x Premium sensitivity matrix and solves for the
break-even synergies required to make the deal EPS-neutral.

Run:
    python ma_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "deal_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k not in ("Acquirer_Name", "Target_Name"):
            a[k] = float(a[k])
    return a


def run_deal(a: dict, cash_pct: float = None, premium: float = None, synergies_override: float = None):
    """Compute pro forma EPS and accretion/dilution for a given set of deal terms.
    Falls back to the base-case assumptions for any parameter not overridden."""
    cash_pct = a["CashPct"] if cash_pct is None else cash_pct
    premium = a["Premium"] if premium is None else premium
    pretax_synergies = a["AnnualPreTaxSynergies_mm"] if synergies_override is None else synergies_override

    offer_price = a["Target_SharePrice_PreDeal"] * (1 + premium)
    purchase_price = offer_price * a["Target_DilutedShares_mm"]

    cash_consideration = purchase_price * cash_pct
    stock_consideration = purchase_price * (1 - cash_pct)

    new_shares_issued = stock_consideration / a["Acquirer_SharePrice"]
    new_debt = cash_consideration  # simplifying assumption: 100% of cash consideration is debt-financed

    after_tax_incremental_interest = new_debt * a["NewDebtInterestRate"] * (1 - a["TaxRate"])
    after_tax_synergies = pretax_synergies * (1 - a["TaxRate"])

    pro_forma_ni = (
        a["Acquirer_NetIncome_mm"]
        + a["Target_NetIncome_mm"]
        + after_tax_synergies
        - after_tax_incremental_interest
    )
    pro_forma_shares = a["Acquirer_DilutedShares_mm"] + new_shares_issued
    pro_forma_eps = pro_forma_ni / pro_forma_shares

    standalone_eps = a["Acquirer_NetIncome_mm"] / a["Acquirer_DilutedShares_mm"]
    accretion_dilution_pct = pro_forma_eps / standalone_eps - 1

    goodwill = purchase_price - a["Target_BookValueEquity_mm"]

    return {
        "offer_price": offer_price,
        "purchase_price": purchase_price,
        "cash_consideration": cash_consideration,
        "stock_consideration": stock_consideration,
        "new_shares_issued": new_shares_issued,
        "new_debt": new_debt,
        "after_tax_incremental_interest": after_tax_incremental_interest,
        "after_tax_synergies": after_tax_synergies,
        "pro_forma_ni": pro_forma_ni,
        "pro_forma_shares": pro_forma_shares,
        "pro_forma_eps": pro_forma_eps,
        "standalone_eps": standalone_eps,
        "accretion_dilution_pct": accretion_dilution_pct,
        "goodwill": goodwill,
    }


def sensitivity_matrix(a: dict) -> pd.DataFrame:
    cash_pcts = [0.0, 0.25, 0.50, 0.75, 1.0]
    premiums = [0.10, 0.20, 0.25, 0.30, 0.40]

    table = pd.DataFrame(index=[f"{c:.0%} cash" for c in cash_pcts],
                          columns=[f"{p:.0%} premium" for p in premiums])
    for c in cash_pcts:
        for p in premiums:
            res = run_deal(a, cash_pct=c, premium=p)
            table.loc[f"{c:.0%} cash", f"{p:.0%} premium"] = round(res["accretion_dilution_pct"] * 100, 1)
    return table


def breakeven_synergies(a: dict, tol: float = 1e-6, max_iter: int = 200) -> float:
    """Binary search for the pre-tax annual synergies at which the deal is exactly EPS-neutral."""
    lo, hi = -500.0, 2000.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        res = run_deal(a, synergies_override=mid)
        if abs(res["accretion_dilution_pct"]) < tol:
            return mid
        if res["accretion_dilution_pct"] < 0:
            lo = mid
        else:
            hi = mid
    return mid


def plot_eps_comparison(base: dict):
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["Acquirer Standalone EPS", "Pro Forma EPS"],
                   [base["standalone_eps"], base["pro_forma_eps"]],
                   color=["#7FA6D9", "#2E5090"])
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:.2f}", (bar.get_x() + bar.get_width() / 2, height),
                    ha="center", va="bottom")
    direction = "Accretive" if base["accretion_dilution_pct"] > 0 else "Dilutive"
    ax.set_title(f"Standalone vs. Pro Forma EPS ({direction} {base['accretion_dilution_pct']:+.1%})")
    ax.set_ylabel("EPS ($)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "eps_comparison.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Accretion / (Dilution) % — Cash Mix x Premium Paid")

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:+.1f}%", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="Accretion / (Dilution) %")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    a = load_assumptions()
    base = run_deal(a)
    sens = sensitivity_matrix(a)
    breakeven = breakeven_synergies(a)

    sens.to_csv(os.path.join(OUTPUT_DIR, "sensitivity_matrix.csv"))

    with open(os.path.join(OUTPUT_DIR, "deal_summary.txt"), "w") as f:
        f.write(f"Acquirer: {a['Acquirer_Name']}\n")
        f.write(f"Target: {a['Target_Name']}\n\n")
        f.write(f"Offer Price per Share: ${base['offer_price']:.2f} ({a['Premium']:.0%} premium)\n")
        f.write(f"Total Purchase Price: ${base['purchase_price']:,.1f}mm\n")
        f.write(f"  Cash Consideration ({a['CashPct']:.0%}): ${base['cash_consideration']:,.1f}mm "
                f"(financed via new debt @ {a['NewDebtInterestRate']:.1%})\n")
        f.write(f"  Stock Consideration ({1-a['CashPct']:.0%}): ${base['stock_consideration']:,.1f}mm "
                f"-> {base['new_shares_issued']:.2f}mm new shares issued\n")
        f.write(f"Implied Goodwill Created: ${base['goodwill']:,.1f}mm\n\n")
        f.write(f"After-tax Annual Synergies: ${base['after_tax_synergies']:,.1f}mm\n")
        f.write(f"After-tax Incremental Interest Expense: ${base['after_tax_incremental_interest']:,.1f}mm\n\n")
        f.write(f"Acquirer Standalone Net Income: ${a['Acquirer_NetIncome_mm']:,.1f}mm\n")
        f.write(f"Acquirer Standalone EPS: ${base['standalone_eps']:.2f}\n")
        f.write(f"Pro Forma Combined Net Income: ${base['pro_forma_ni']:,.1f}mm\n")
        f.write(f"Pro Forma Diluted Shares: {base['pro_forma_shares']:.2f}mm\n")
        f.write(f"Pro Forma EPS: ${base['pro_forma_eps']:.2f}\n")
        f.write(f"Accretion / (Dilution): {base['accretion_dilution_pct']:+.2%}\n\n")
        f.write(f"Break-even annual pre-tax synergies (EPS-neutral): ${breakeven:,.1f}mm\n")
        f.write(f"(Base case assumes ${a['AnnualPreTaxSynergies_mm']:,.0f}mm pre-tax synergies -> "
                f"deal is {'accretive' if base['accretion_dilution_pct'] > 0 else 'dilutive'} "
                f"with headroom of ${a['AnnualPreTaxSynergies_mm'] - breakeven:,.1f}mm before turning dilutive)\n"
                if base["accretion_dilution_pct"] > 0 else "")
        f.write(f"\nOne-time deal/integration costs (excluded from recurring pro forma EPS): "
                f"${a['OneTimeDealCosts_mm']:,.0f}mm\n")

    plot_eps_comparison(base)
    plot_sensitivity_heatmap(sens)

    print(f"=== M&A Accretion / Dilution: {a['Acquirer_Name']} acquires {a['Target_Name']} ===")
    print(f"Offer Price: ${base['offer_price']:.2f}  |  Purchase Price: ${base['purchase_price']:,.1f}mm  "
          f"|  Goodwill: ${base['goodwill']:,.1f}mm")
    print(f"Standalone EPS: ${base['standalone_eps']:.2f}  ->  Pro Forma EPS: ${base['pro_forma_eps']:.2f}")
    print(f"Accretion / (Dilution): {base['accretion_dilution_pct']:+.2%}")
    print(f"Break-even pre-tax synergies: ${breakeven:,.1f}mm (base case assumes ${a['AnnualPreTaxSynergies_mm']:,.0f}mm)")
    print("\n=== Sensitivity: Accretion/(Dilution) % by Cash Mix x Premium ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
