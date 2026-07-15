"""
Discounted Cash Flow (DCF) Model - Semiconductor Sector (Texas Instruments, TXN)

Builds a 5-year unlevered free cash flow forecast, discounts it at WACC (derived
via CAPM), computes a Gordon Growth terminal value, and backs into an implied
share price. Also produces a WACC x terminal-growth sensitivity table.

Run:
    python dcf_model.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "dcf_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    numeric_keys = [k for k in a if k not in ("Company",)]
    for k in numeric_keys:
        a[k] = float(a[k])
    a["ForecastYears"] = int(a["ForecastYears"])
    return a


def load_drivers() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "forecast_drivers.csv")
    return pd.read_csv(path)


def compute_wacc(a: dict) -> float:
    cost_of_equity = a["RiskFreeRate"] + a["Beta"] * a["EquityRiskPremium"]
    after_tax_cost_of_debt = a["PreTaxCostOfDebt"] * (1 - a["TaxRate"])
    wacc = a["EquityWeight"] * cost_of_equity + a["DebtWeight"] * after_tax_cost_of_debt
    return wacc, cost_of_equity, after_tax_cost_of_debt


def build_forecast(a: dict, drivers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    revenue = a["BaseRevenue_mm"]
    for _, d in drivers.iterrows():
        revenue = revenue * (1 + d["RevenueGrowth"])
        ebit = revenue * d["EBITMargin"]
        tax_on_ebit = ebit * a["TaxRate"]
        nopat = ebit - tax_on_ebit
        da = revenue * d["DA_pctRevenue"]
        capex = revenue * d["Capex_pctRevenue"]
        delta_nwc = revenue * d["NWC_pctRevenue"]
        ufcf = nopat + da - capex - delta_nwc

        rows.append({
            "Year": int(d["Year"]),
            "Revenue_mm": revenue,
            "EBIT_mm": ebit,
            "NOPAT_mm": nopat,
            "D&A_mm": da,
            "Capex_mm": capex,
            "DeltaNWC_mm": delta_nwc,
            "UFCF_mm": ufcf,
        })
    return pd.DataFrame(rows)


def discount_cash_flows(forecast: pd.DataFrame, wacc: float, terminal_growth: float, net_debt: float,
                         shares_out: float):
    forecast = forecast.copy()
    forecast["DiscountFactor"] = 1 / (1 + wacc) ** forecast["Year"]
    forecast["PV_UFCF_mm"] = forecast["UFCF_mm"] * forecast["DiscountFactor"]

    final_year_fcf = forecast["UFCF_mm"].iloc[-1]
    terminal_value = final_year_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value * forecast["DiscountFactor"].iloc[-1]

    sum_pv_fcf = forecast["PV_UFCF_mm"].sum()
    enterprise_value = sum_pv_fcf + pv_terminal_value
    equity_value = enterprise_value - net_debt
    implied_share_price = equity_value / shares_out

    results = {
        "sum_pv_fcf": sum_pv_fcf,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "implied_share_price": implied_share_price,
        "pct_ev_from_terminal": pv_terminal_value / enterprise_value,
    }
    return forecast, results


def sensitivity_table(forecast: pd.DataFrame, base_wacc: float, base_g: float, net_debt: float,
                       shares_out: float) -> pd.DataFrame:
    wacc_range = [base_wacc + delta for delta in (-0.010, -0.005, 0.0, 0.005, 0.010)]
    g_range = [base_g + delta for delta in (-0.010, -0.005, 0.0, 0.005, 0.010)]

    table = pd.DataFrame(index=[f"{w:.2%}" for w in wacc_range], columns=[f"{g:.2%}" for g in g_range])

    for w in wacc_range:
        for g in g_range:
            _, res = discount_cash_flows(forecast, w, g, net_debt, shares_out)
            table.loc[f"{w:.2%}", f"{g:.2%}"] = round(res["implied_share_price"], 2)

    table.index.name = "WACC"
    table.columns.name = "Terminal Growth"
    return table


def plot_fcf_bridge(forecast: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(forecast["Year"], forecast["UFCF_mm"], color="#2E5090", label="Unlevered FCF")
    ax.bar(forecast["Year"], forecast["PV_UFCF_mm"], color="#7FA6D9", label="PV of UFCF")
    ax.set_xlabel("Forecast Year")
    ax.set_ylabel("$mm")
    ax.set_title("TXN - Unlevered FCF Forecast vs. Present Value")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fcf_forecast.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns)
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_xlabel("Terminal Growth Rate")
    ax.set_ylabel("WACC")
    ax.set_title("Implied Share Price Sensitivity ($)")

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="Implied Share Price ($)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    a = load_assumptions()
    drivers = load_drivers()

    wacc, cost_of_equity, after_tax_cod = compute_wacc(a)
    forecast = build_forecast(a, drivers)
    net_debt = a["TotalDebt_mm"] - a["CashAndInvestments_mm"]

    forecast, results = discount_cash_flows(
        forecast, wacc, a["TerminalGrowthRate"], net_debt, a["SharesOutstanding_mm"]
    )
    sens_table = sensitivity_table(forecast, wacc, a["TerminalGrowthRate"], net_debt, a["SharesOutstanding_mm"])

    forecast.round(2).to_csv(os.path.join(OUTPUT_DIR, "fcf_forecast.csv"), index=False)
    sens_table.to_csv(os.path.join(OUTPUT_DIR, "sensitivity_table.csv"))

    with open(os.path.join(OUTPUT_DIR, "dcf_summary.txt"), "w") as f:
        f.write(f"Company: {a['Company']}\n")
        f.write(f"Cost of Equity (CAPM): {cost_of_equity:.2%}\n")
        f.write(f"After-tax Cost of Debt: {after_tax_cod:.2%}\n")
        f.write(f"WACC: {wacc:.2%}\n")
        f.write(f"Terminal Growth Rate: {a['TerminalGrowthRate']:.2%}\n\n")
        f.write(f"Sum of PV of FCFs: ${results['sum_pv_fcf']:,.0f}mm\n")
        f.write(f"Terminal Value (undiscounted): ${results['terminal_value']:,.0f}mm\n")
        f.write(f"PV of Terminal Value: ${results['pv_terminal_value']:,.0f}mm\n")
        f.write(f"% of EV from Terminal Value: {results['pct_ev_from_terminal']:.1%}\n\n")
        f.write(f"Enterprise Value: ${results['enterprise_value']:,.0f}mm\n")
        f.write(f"Net Debt: ${net_debt:,.0f}mm\n")
        f.write(f"Equity Value: ${results['equity_value']:,.0f}mm\n")
        f.write(f"Shares Outstanding: {a['SharesOutstanding_mm']:,.0f}mm\n")
        f.write(f"Implied Share Price: ${results['implied_share_price']:.2f}\n")

    plot_fcf_bridge(forecast)
    plot_sensitivity_heatmap(sens_table)

    print(f"=== DCF Summary: {a['Company']} ===")
    print(f"WACC: {wacc:.2%}  |  Terminal Growth: {a['TerminalGrowthRate']:.2%}")
    print(f"\n=== Forecast ===")
    print(forecast.round(1).to_string(index=False))
    print(f"\nEnterprise Value: ${results['enterprise_value']:,.0f}mm")
    print(f"Equity Value: ${results['equity_value']:,.0f}mm")
    print(f"Implied Share Price: ${results['implied_share_price']:.2f}")
    print(f"% of EV from Terminal Value: {results['pct_ev_from_terminal']:.1%}")
    print(f"\n=== Sensitivity Table (Implied Share Price) ===")
    print(sens_table.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
