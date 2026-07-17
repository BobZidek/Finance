"""
IPO Valuation & Readiness Model - Nimbus Cloud Systems

Builds a comps-based intrinsic valuation range, sets an IPO offer price
at a standard underwriting discount to the intrinsic midpoint, and models
the full IPO mechanics: primary vs. secondary shares, the greenshoe
over-allotment option, underwriting fees, net proceeds to the company,
post-IPO dilution and public float, and the "money left on the table"
from intentional IPO underpricing.

Run:
    python ipo_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "ipo_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    a["PreIPOSharesOutstanding"] = int(a["PreIPOSharesOutstanding"])
    a["PrimarySharesOffered"] = int(a["PrimarySharesOffered"])
    a["SecondarySharesOffered"] = int(a["SecondarySharesOffered"])
    return a


def compute_intrinsic_range(a: dict) -> dict:
    low_ev = a["LowMultiple_EVRevenue"] * a["LTMRevenue_mm"]
    high_ev = a["HighMultiple_EVRevenue"] * a["LTMRevenue_mm"]
    mid_ev = (low_ev + high_ev) / 2

    low_equity = (low_ev + a["PreIPONetCash_mm"]) * 1_000_000
    high_equity = (high_ev + a["PreIPONetCash_mm"]) * 1_000_000
    mid_equity = (mid_ev + a["PreIPONetCash_mm"]) * 1_000_000

    low_ps = low_equity / a["PreIPOSharesOutstanding"]
    high_ps = high_equity / a["PreIPOSharesOutstanding"]
    mid_ps = mid_equity / a["PreIPOSharesOutstanding"]

    return {"low_ev": low_ev, "high_ev": high_ev, "mid_ev": mid_ev,
            "low_ps": low_ps, "high_ps": high_ps, "mid_ps": mid_ps}


def compute_ipo_mechanics(a: dict, intrinsic_mid_ps: float, offer_price: float = None) -> dict:
    offer_price = a["IPOOfferPrice"] if offer_price is None else offer_price

    base_offered = a["PrimarySharesOffered"] + a["SecondarySharesOffered"]
    greenshoe_shares = int(base_offered * a["GreenshoePct"])  # assumed fully primary
    total_primary = a["PrimarySharesOffered"] + greenshoe_shares
    total_offered_with_greenshoe = base_offered + greenshoe_shares

    gross_primary_proceeds = total_primary * offer_price
    underwriting_fee = gross_primary_proceeds * a["UnderwritingDiscountPct"]
    net_primary_proceeds = gross_primary_proceeds - underwriting_fee

    post_ipo_shares = a["PreIPOSharesOutstanding"] + total_primary
    post_ipo_market_cap = post_ipo_shares * offer_price
    post_ipo_market_cap_at_intrinsic = post_ipo_shares * intrinsic_mid_ps

    existing_holder_ownership_pct = a["PreIPOSharesOutstanding"] / post_ipo_shares
    public_float_pct = total_offered_with_greenshoe / post_ipo_shares

    money_left_on_table = (intrinsic_mid_ps - offer_price) * total_offered_with_greenshoe

    return {
        "offer_price": offer_price, "greenshoe_shares": greenshoe_shares,
        "total_primary": total_primary, "total_offered_with_greenshoe": total_offered_with_greenshoe,
        "gross_primary_proceeds": gross_primary_proceeds, "underwriting_fee": underwriting_fee,
        "net_primary_proceeds": net_primary_proceeds, "post_ipo_shares": post_ipo_shares,
        "post_ipo_market_cap": post_ipo_market_cap,
        "post_ipo_market_cap_at_intrinsic": post_ipo_market_cap_at_intrinsic,
        "existing_holder_ownership_pct": existing_holder_ownership_pct,
        "public_float_pct": public_float_pct, "money_left_on_table": money_left_on_table,
    }


def price_sensitivity(a: dict, intrinsic_mid_ps: float) -> pd.DataFrame:
    prices = [16.00, 17.00, 18.00, 19.00, 20.00, 21.00, 22.00]
    rows = []
    for p in prices:
        res = compute_ipo_mechanics(a, intrinsic_mid_ps, offer_price=p)
        rows.append({"OfferPrice": p, "PostIPOMarketCap_mm": res["post_ipo_market_cap"] / 1_000_000,
                     "NetPrimaryProceeds_mm": res["net_primary_proceeds"] / 1_000_000,
                     "ExistingHolderOwnership_pct": res["existing_holder_ownership_pct"] * 100,
                     "MoneyLeftOnTable_mm": res["money_left_on_table"] / 1_000_000})
    return pd.DataFrame(rows)


def plot_valuation_range(intrinsic: dict, ipo: dict, a: dict):
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["Low\n(6.0x)", "Offer Price\n(underwritten)", "Mid\n(7.5x)", "High\n(9.0x)"]
    values = [intrinsic["low_ps"], ipo["offer_price"], intrinsic["mid_ps"], intrinsic["high_ps"]]
    colors = ["#7FA6D9", "#C0392B", "#2E5090", "#7FA6D9"]
    bars = ax.bar(labels, values, color=colors)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:.2f}", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("Value per Share ($)")
    ax.set_title(f"IPO Pricing vs. Comps-Implied Intrinsic Range - {a['CompanyName']}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "valuation_range.png"), dpi=150)
    plt.close(fig)


def plot_ownership_and_float(ipo: dict):
    fig, ax = plt.subplots(figsize=(7, 6))
    labels = ["Existing Holders\n(post-IPO)", "Public Float"]
    values = [ipo["existing_holder_ownership_pct"] * 100, ipo["public_float_pct"] * 100]
    ax.pie(values, labels=labels, autopct="%1.1f%%", colors=["#2E5090", "#7FA6D9"])
    ax.set_title("Post-IPO Ownership Split")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "ownership_split.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    intrinsic = compute_intrinsic_range(a)
    ipo = compute_ipo_mechanics(a, intrinsic["mid_ps"])
    sens = price_sensitivity(a, intrinsic["mid_ps"])
    sens.round(2).to_csv(os.path.join(OUTPUT_DIR, "price_sensitivity.csv"), index=False)

    discount_to_intrinsic = 1 - ipo["offer_price"] / intrinsic["mid_ps"]

    with open(os.path.join(OUTPUT_DIR, "ipo_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write("=== Comps-Based Intrinsic Valuation Range ===\n")
        f.write(f"EV Range: ${intrinsic['low_ev']:,.0f}mm - ${intrinsic['high_ev']:,.0f}mm "
                f"({a['LowMultiple_EVRevenue']:.1f}x - {a['HighMultiple_EVRevenue']:.1f}x LTM Revenue)\n")
        f.write(f"Per-Share Range: ${intrinsic['low_ps']:.2f} - ${intrinsic['high_ps']:.2f} "
                f"(midpoint ${intrinsic['mid_ps']:.2f})\n\n")
        f.write("=== IPO Pricing & Mechanics ===\n")
        f.write(f"IPO Offer Price: ${ipo['offer_price']:.2f} "
                f"({discount_to_intrinsic:.1%} discount to intrinsic midpoint - standard underwriting practice)\n")
        f.write(f"Primary Shares Offered: {a['PrimarySharesOffered']:,}\n")
        f.write(f"Secondary Shares Offered: {a['SecondarySharesOffered']:,}\n")
        f.write(f"Greenshoe (over-allotment, {a['GreenshoePct']:.0%}): {ipo['greenshoe_shares']:,} shares "
                f"(assumed primary)\n")
        f.write(f"Total Primary Shares (incl. greenshoe): {ipo['total_primary']:,}\n")
        f.write(f"Total Shares Sold in Offering: {ipo['total_offered_with_greenshoe']:,}\n\n")
        f.write(f"Gross Primary Proceeds: ${ipo['gross_primary_proceeds']:,.0f}\n")
        f.write(f"Underwriting Fee ({a['UnderwritingDiscountPct']:.1%}): -${ipo['underwriting_fee']:,.0f}\n")
        f.write(f"Net Primary Proceeds to Company: ${ipo['net_primary_proceeds']:,.0f}\n\n")
        f.write(f"Post-IPO Shares Outstanding: {ipo['post_ipo_shares']:,}\n")
        f.write(f"Post-IPO Market Cap (at offer price): ${ipo['post_ipo_market_cap']:,.0f}\n")
        f.write(f"Post-IPO Market Cap (if trades to intrinsic midpoint): "
                f"${ipo['post_ipo_market_cap_at_intrinsic']:,.0f}\n\n")
        f.write(f"Existing Holder Ownership (post-IPO): {ipo['existing_holder_ownership_pct']:.1%}\n")
        f.write(f"Public Float: {ipo['public_float_pct']:.1%}\n\n")
        f.write(f"Money Left on the Table (at intrinsic midpoint): ${ipo['money_left_on_table']:,.0f}\n")

    plot_valuation_range(intrinsic, ipo, a)
    plot_ownership_and_float(ipo)

    print(f"=== IPO Valuation & Readiness: {a['CompanyName']} ===")
    print(f"Intrinsic Range: ${intrinsic['low_ps']:.2f} - ${intrinsic['high_ps']:.2f} "
          f"(mid ${intrinsic['mid_ps']:.2f})")
    print(f"IPO Offer Price: ${ipo['offer_price']:.2f} ({discount_to_intrinsic:.1%} discount)\n")
    print(f"Net Primary Proceeds: ${ipo['net_primary_proceeds']:,.0f}")
    print(f"Post-IPO Market Cap: ${ipo['post_ipo_market_cap']:,.0f}")
    print(f"Existing Holder Ownership: {ipo['existing_holder_ownership_pct']:.1%}  |  "
          f"Public Float: {ipo['public_float_pct']:.1%}")
    print(f"Money Left on the Table: ${ipo['money_left_on_table']:,.0f}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
