"""
Merger Model with Synergies - Airlines

Models a hypothetical stock + cash merger between two fictional airlines,
with a 3-year synergy ramp (cost and revenue synergies realized at
different rates), multi-year pro forma EPS accretion/dilution, and pro
forma leverage (Net Debt / EBITDA) deleveraging over the forecast period.

Run:
    python merger_model.py
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


def load_ramp() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "synergy_ramp.csv"))


def deal_structure(a: dict, cash_pct: float = None):
    cash_pct = a["CashPct"] if cash_pct is None else cash_pct

    offer_price = a["Target_SharePrice_PreDeal"] * (1 + a["Premium"])
    purchase_equity_value = offer_price * a["Target_DilutedShares_mm"]

    cash_consideration = purchase_equity_value * cash_pct
    stock_consideration = purchase_equity_value * (1 - cash_pct)
    new_shares_issued = stock_consideration / a["Acquirer_SharePrice"]
    new_deal_debt = cash_consideration  # cash portion financed with new debt

    return {
        "offer_price": offer_price,
        "purchase_equity_value": purchase_equity_value,
        "cash_consideration": cash_consideration,
        "stock_consideration": stock_consideration,
        "new_shares_issued": new_shares_issued,
        "new_deal_debt": new_deal_debt,
    }


def base_financials(a: dict):
    acq_ebit = a["Acquirer_Revenue_mm"] * a["Acquirer_EBITMargin"]
    acq_da = a["Acquirer_Revenue_mm"] * a["Acquirer_DA_pctRevenue"]
    acq_ebitda = acq_ebit + acq_da
    acq_ebt = acq_ebit - a["Acquirer_InterestExpense_mm"]
    acq_ni = acq_ebt * (1 - a["TaxRate"])
    acq_standalone_eps = acq_ni / a["Acquirer_DilutedShares_mm"]

    tgt_ebit = a["Target_Revenue_mm"] * a["Target_EBITMargin"]
    tgt_da = a["Target_Revenue_mm"] * a["Target_DA_pctRevenue"]
    tgt_ebitda = tgt_ebit + tgt_da

    return {
        "acq_ebit": acq_ebit, "acq_da": acq_da, "acq_ebitda": acq_ebitda,
        "acq_standalone_eps": acq_standalone_eps,
        "tgt_ebit": tgt_ebit, "tgt_da": tgt_da, "tgt_ebitda": tgt_ebitda,
    }


def run_pro_forma(a: dict, ramp: pd.DataFrame, cash_pct: float = None,
                   synergy_multiplier: float = 1.0) -> pd.DataFrame:
    ds = deal_structure(a, cash_pct)
    bf = base_financials(a)

    combined_ebit_pre_synergy = bf["acq_ebit"] + bf["tgt_ebit"]
    combined_ebitda_pre_synergy = bf["acq_ebitda"] + bf["tgt_ebitda"]
    combined_interest = (
        a["Acquirer_InterestExpense_mm"]
        + a["Target_InterestExpense_mm"]
        + ds["new_deal_debt"] * a["NewDebtInterestRate"]
    )
    combined_net_debt = a["Acquirer_NetDebt_mm"] + a["Target_NetDebt_mm"] + ds["new_deal_debt"]
    pro_forma_shares = a["Acquirer_DilutedShares_mm"] + ds["new_shares_issued"]

    rows = []
    for _, r in ramp.iterrows():
        cost_synergy = a["CostSynergyRunRate_mm"] * r["CostSynergyRealization"] * synergy_multiplier
        revenue_synergy_ebit = (a["RevenueSynergyRunRate_mm"] * r["RevenueSynergyRealization"]
                                 * a["RevenueSynergyFlowThroughMargin"] * synergy_multiplier)
        total_synergy_ebit = cost_synergy + revenue_synergy_ebit

        combined_ebit = combined_ebit_pre_synergy + total_synergy_ebit
        combined_ebitda = combined_ebitda_pre_synergy + total_synergy_ebit
        ebt = combined_ebit - combined_interest
        ni = ebt * (1 - a["TaxRate"])
        pro_forma_eps = ni / pro_forma_shares
        accretion_dilution = pro_forma_eps / bf["acq_standalone_eps"] - 1
        leverage = combined_net_debt / combined_ebitda

        integration_cost = a["OneTimeIntegrationCosts_mm"] * r["IntegrationCostRealization"]

        rows.append({
            "Year": int(r["Year"]),
            "CostSynergy_mm": cost_synergy,
            "RevenueSynergyEBIT_mm": revenue_synergy_ebit,
            "CombinedEBIT_mm": combined_ebit,
            "CombinedEBITDA_mm": combined_ebitda,
            "CombinedInterest_mm": combined_interest,
            "ProFormaNetIncome_mm": ni,
            "ProFormaEPS": pro_forma_eps,
            "AccretionDilution_pct": accretion_dilution * 100,
            "ProFormaLeverage_x": leverage,
            "OneTimeIntegrationCost_mm": integration_cost,
        })

    forecast = pd.DataFrame(rows)
    return ds, bf, forecast


def sensitivity_grid(a: dict, ramp: pd.DataFrame) -> pd.DataFrame:
    synergy_mults = [0.5, 0.75, 1.0, 1.25, 1.5]
    cash_pcts = [0.0, 0.25, 0.40, 0.60, 0.75, 1.0]
    table = pd.DataFrame(index=[f"{s:.0%} synergy realization" for s in synergy_mults],
                          columns=[f"{c:.0%} cash" for c in cash_pcts])
    for s in synergy_mults:
        for c in cash_pcts:
            _, _, forecast = run_pro_forma(a, ramp, cash_pct=c, synergy_multiplier=s)
            year3 = forecast[forecast["Year"] == 3].iloc[0]
            table.loc[f"{s:.0%} synergy realization", f"{c:.0%} cash"] = round(year3["AccretionDilution_pct"], 1)
    return table


def plot_eps_accretion(forecast: pd.DataFrame, standalone_eps: float):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(forecast["Year"], forecast["ProFormaEPS"], marker="o", color="#2E5090", label="Pro Forma EPS")
    ax.axhline(standalone_eps, color="grey", linestyle="--", label=f"Acquirer Standalone EPS (${standalone_eps:.2f})")
    ax.set_xlabel("Year Post-Close")
    ax.set_ylabel("EPS ($)")
    ax.set_title("Pro Forma EPS vs. Acquirer Standalone EPS")
    ax.set_xticks(forecast["Year"])
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "eps_accretion.png"), dpi=150)
    plt.close(fig)


def plot_leverage(forecast: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(forecast["Year"], forecast["ProFormaLeverage_x"], color="#7FA6D9")
    ax.set_xlabel("Year Post-Close")
    ax.set_ylabel("Net Debt / EBITDA (x)")
    ax.set_title("Pro Forma Leverage")
    ax.set_xticks(forecast["Year"])
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "leverage.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Year 3 Accretion / (Dilution) % — Synergy Realization x Cash Mix")
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
    ramp = load_ramp()

    ds, bf, forecast = run_pro_forma(a, ramp)
    sens = sensitivity_grid(a, ramp)

    forecast.round(2).to_csv(os.path.join(OUTPUT_DIR, "pro_forma_forecast.csv"), index=False)
    sens.to_csv(os.path.join(OUTPUT_DIR, "sensitivity_matrix.csv"))

    with open(os.path.join(OUTPUT_DIR, "merger_summary.txt"), "w") as f:
        f.write(f"Acquirer: {a['Acquirer_Name']}\n")
        f.write(f"Target: {a['Target_Name']}\n\n")
        f.write(f"Offer Price per Share: ${ds['offer_price']:.2f} ({a['Premium']:.0%} premium)\n")
        f.write(f"Purchase Equity Value: ${ds['purchase_equity_value']:,.1f}mm\n")
        f.write(f"  Cash Consideration ({a['CashPct']:.0%}): ${ds['cash_consideration']:,.1f}mm "
                f"(new debt @ {a['NewDebtInterestRate']:.1%})\n")
        f.write(f"  Stock Consideration ({1-a['CashPct']:.0%}): ${ds['stock_consideration']:,.1f}mm "
                f"-> {ds['new_shares_issued']:.2f}mm new shares issued\n\n")
        f.write(f"Acquirer Standalone EPS: ${bf['acq_standalone_eps']:.2f}\n\n")
        f.write("=== 3-Year Pro Forma ===\n")
        f.write(forecast.round(2).to_string(index=False))
        f.write(f"\n\nOne-time integration costs (${a['OneTimeIntegrationCosts_mm']:,.0f}mm total, "
                f"excluded from recurring pro forma EPS above) are phased 60% Year 1 / 40% Year 2.\n")

    plot_eps_accretion(forecast, bf["acq_standalone_eps"])
    plot_leverage(forecast)
    plot_sensitivity_heatmap(sens)

    print(f"=== Merger Model: {a['Acquirer_Name']} + {a['Target_Name']} ===")
    print(f"Offer Price: ${ds['offer_price']:.2f}  |  Purchase Equity Value: ${ds['purchase_equity_value']:,.1f}mm")
    print(f"Acquirer Standalone EPS: ${bf['acq_standalone_eps']:.2f}\n")
    print(forecast.round(2).to_string(index=False))
    print("\n=== Sensitivity: Year 3 Accretion/(Dilution) % — Synergy Realization x Cash Mix ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
