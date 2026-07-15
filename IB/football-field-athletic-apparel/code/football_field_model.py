"""
Football Field Valuation - Athletic Apparel

Combines three valuation methodologies for a hypothetical private athletic
apparel target - trading comps, precedent M&A transactions, and a DCF - and
plots the resulting implied Enterprise Value ranges on a single "football
field" chart, the standard way banks present a valuation conclusion.

Run:
    python football_field_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_target() -> dict:
    path = os.path.join(DATA_DIR, "target_and_dcf.csv")
    df = pd.read_csv(path, index_col="Field")
    t = {k: v for k, v in df["Value"].items()}
    for k in t:
        if k != "TargetName":
            t[k] = float(t[k])
    return t


# ---------------------------------------------------------------------------
# Method 1: Trading comps
# ---------------------------------------------------------------------------

def trading_comps_range(target: dict) -> dict:
    df = pd.read_csv(os.path.join(DATA_DIR, "trading_comps.csv"))
    df["MarketCap_mm"] = df["Price"] * df["SharesOut_mm"]
    df["EV_mm"] = df["MarketCap_mm"] + df["TotalDebt_mm"] - df["Cash_mm"]
    df["EV_Revenue"] = df["EV_mm"] / df["Revenue_LTM_mm"]
    df["EV_EBITDA"] = df["EV_mm"] / df["EBITDA_LTM_mm"]

    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "trading_comps_detail.csv"), index=False)

    low = df["EV_EBITDA"].quantile(0.25) * target["EBITDA_LTM_mm"]
    high = df["EV_EBITDA"].quantile(0.75) * target["EBITDA_LTM_mm"]
    mid = df["EV_EBITDA"].median() * target["EBITDA_LTM_mm"]
    return {"method": "Trading Comps (EV/EBITDA)", "low": low, "mid": mid, "high": high,
            "low_mult": df["EV_EBITDA"].quantile(0.25), "high_mult": df["EV_EBITDA"].quantile(0.75)}


# ---------------------------------------------------------------------------
# Method 2: Precedent transactions
# ---------------------------------------------------------------------------

def precedent_transactions_range(target: dict) -> dict:
    df = pd.read_csv(os.path.join(DATA_DIR, "precedent_transactions.csv"))
    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "precedent_transactions_detail.csv"), index=False)

    low = df["EV_EBITDA"].quantile(0.25) * target["EBITDA_LTM_mm"]
    high = df["EV_EBITDA"].quantile(0.75) * target["EBITDA_LTM_mm"]
    mid = df["EV_EBITDA"].median() * target["EBITDA_LTM_mm"]
    return {"method": "Precedent Transactions (EV/EBITDA)", "low": low, "mid": mid, "high": high,
            "low_mult": df["EV_EBITDA"].quantile(0.25), "high_mult": df["EV_EBITDA"].quantile(0.75)}


# ---------------------------------------------------------------------------
# Method 3: DCF
# ---------------------------------------------------------------------------

def dcf_range(target: dict) -> dict:
    revenue = target["Revenue_LTM_mm"]
    growth_rates = [target["RevenueGrowthY1"], target["RevenueGrowthY2"], target["RevenueGrowthY3"],
                     target["RevenueGrowthY4"], target["RevenueGrowthY5"]]

    start_margin = target["EBITDA_LTM_mm"] / target["Revenue_LTM_mm"]
    end_margin = target["EBITDAMarginTerminal"]

    rows = []
    for i, g in enumerate(growth_rates, start=1):
        revenue = revenue * (1 + g)
        margin = start_margin + (end_margin - start_margin) * (i / len(growth_rates))
        ebitda = revenue * margin
        da = revenue * target["DA_pctRevenue"]
        ebit = ebitda - da
        nopat = ebit * (1 - target["TaxRate"])
        capex = revenue * target["Capex_pctRevenue"]
        delta_nwc = revenue * target["NWC_pctRevenue"]
        ufcf = nopat + da - capex - delta_nwc
        rows.append({"Year": i, "Revenue_mm": revenue, "EBITDA_mm": ebitda, "UFCF_mm": ufcf})

    forecast = pd.DataFrame(rows)
    wacc = target["WACC"]
    g_term = target["TerminalGrowthRate"]

    forecast["DiscountFactor"] = 1 / (1 + wacc) ** forecast["Year"]
    forecast["PV_UFCF_mm"] = forecast["UFCF_mm"] * forecast["DiscountFactor"]

    terminal_value = forecast["UFCF_mm"].iloc[-1] * (1 + g_term) / (wacc - g_term)
    pv_terminal_value = terminal_value * forecast["DiscountFactor"].iloc[-1]

    base_ev = forecast["PV_UFCF_mm"].sum() + pv_terminal_value

    # Range from a WACC +/- 0.75% sensitivity band
    def ev_at(w):
        disc = [1 / (1 + w) ** y for y in forecast["Year"]]
        pv_fcf = sum(f * d for f, d in zip(forecast["UFCF_mm"], disc))
        tv = forecast["UFCF_mm"].iloc[-1] * (1 + g_term) / (w - g_term)
        return pv_fcf + tv * disc[-1]

    ev_low = ev_at(wacc + 0.0075)   # higher discount rate -> lower value
    ev_high = ev_at(wacc - 0.0075)  # lower discount rate -> higher value

    forecast.round(2).to_csv(os.path.join(OUTPUT_DIR, "dcf_forecast_detail.csv"), index=False)

    return {"method": "DCF (WACC +/- 0.75%)", "low": ev_low, "mid": base_ev, "high": ev_high,
            "low_mult": None, "high_mult": None}


def plot_football_field(results: list, target_name: str):
    fig, ax = plt.subplots(figsize=(9, 4))
    methods = [r["method"] for r in results][::-1]
    lows = [r["low"] for r in results][::-1]
    highs = [r["high"] for r in results][::-1]
    mids = [r["mid"] for r in results][::-1]

    for i, (lo, hi, mid) in enumerate(zip(lows, highs, mids)):
        ax.barh(i, hi - lo, left=lo, height=0.45, color="#7FA6D9", edgecolor="#2E5090")
        ax.plot(mid, i, "o", color="#2E5090")
        ax.text(hi + 15, i, f"${lo:,.0f}mm - ${hi:,.0f}mm", va="center", fontsize=9)

    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels(methods)
    ax.set_xlabel("Implied Enterprise Value ($mm)")
    ax.set_title(f"Football Field Valuation - {target_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "football_field.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = load_target()

    comps_res = trading_comps_range(target)
    prec_res = precedent_transactions_range(target)
    dcf_res = dcf_range(target)

    results = [comps_res, prec_res, dcf_res]
    summary = pd.DataFrame(results)
    summary.round(1).to_csv(os.path.join(OUTPUT_DIR, "football_field_summary.csv"), index=False)

    plot_football_field(results, target["TargetName"])

    overall_low = min(r["low"] for r in results)
    overall_high = max(r["high"] for r in results)

    with open(os.path.join(OUTPUT_DIR, "valuation_summary.txt"), "w") as f:
        f.write(f"Target: {target['TargetName']}\n\n")
        for r in results:
            f.write(f"{r['method']}: ${r['low']:,.0f}mm - ${r['high']:,.0f}mm  (midpoint ${r['mid']:,.0f}mm)\n")
        f.write(f"\nOverall implied EV range across all methods: ${overall_low:,.0f}mm - ${overall_high:,.0f}mm\n")
        f.write(f"Overall implied Equity Value range (EV - Net Debt of ${target['NetDebt_mm']:,.0f}mm): "
                f"${overall_low - target['NetDebt_mm']:,.0f}mm - ${overall_high - target['NetDebt_mm']:,.0f}mm\n")

    print(f"=== Football Field Valuation: {target['TargetName']} ===\n")
    for r in results:
        print(f"{r['method']:40s}  ${r['low']:>8,.0f}mm  -  ${r['high']:>8,.0f}mm   (mid ${r['mid']:,.0f}mm)")
    print(f"\nOverall EV range: ${overall_low:,.0f}mm - ${overall_high:,.0f}mm")
    print(f"Overall Equity Value range: ${overall_low - target['NetDebt_mm']:,.0f}mm - "
          f"${overall_high - target['NetDebt_mm']:,.0f}mm")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
