"""
Full Pitch Book - Industrials / Logistics

The capstone IB project: combines four valuation methodologies for a
hypothetical private 3PL / freight brokerage and warehousing target -
trading comps, precedent M&A transactions, a DCF, and an LBO "ability to
pay" analysis (the maximum entry multiple a financial sponsor could pay
and still clear a target IRR) - into a single four-bar football field,
plus a written industry overview and recommendation.

Run:
    python pitch_book.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_target() -> dict:
    path = os.path.join(DATA_DIR, "target_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    t = {k: v for k, v in df["Value"].items()}
    for k in t:
        if k != "TargetName":
            t[k] = float(t[k])
    t["LBO_HoldPeriodYears"] = int(t["LBO_HoldPeriodYears"])
    return t


# ---------------------------------------------------------------------------
# Method 1: Trading comps
# ---------------------------------------------------------------------------

def trading_comps_range(target: dict) -> dict:
    df = pd.read_csv(os.path.join(DATA_DIR, "trading_comps.csv"))
    df["MarketCap_mm"] = df["Price"] * df["SharesOut_mm"]
    df["EV_mm"] = df["MarketCap_mm"] + df["TotalDebt_mm"] - df["Cash_mm"]
    df["EV_EBITDA"] = df["EV_mm"] / df["EBITDA_LTM_mm"]
    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "trading_comps_detail.csv"), index=False)

    low = df["EV_EBITDA"].quantile(0.25) * target["EBITDA_LTM_mm"]
    high = df["EV_EBITDA"].quantile(0.75) * target["EBITDA_LTM_mm"]
    mid = df["EV_EBITDA"].median() * target["EBITDA_LTM_mm"]
    return {"method": "Trading Comps", "low": low, "mid": mid, "high": high}


# ---------------------------------------------------------------------------
# Method 2: Precedent transactions
# ---------------------------------------------------------------------------

def precedent_transactions_range(target: dict) -> dict:
    df = pd.read_csv(os.path.join(DATA_DIR, "precedent_transactions.csv"))
    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "precedent_transactions_detail.csv"), index=False)

    low = df["EV_EBITDA"].quantile(0.25) * target["EBITDA_LTM_mm"]
    high = df["EV_EBITDA"].quantile(0.75) * target["EBITDA_LTM_mm"]
    mid = df["EV_EBITDA"].median() * target["EBITDA_LTM_mm"]
    return {"method": "Precedent Transactions", "low": low, "mid": mid, "high": high}


# ---------------------------------------------------------------------------
# Method 3: DCF
# ---------------------------------------------------------------------------

def _dcf_forecast(target: dict):
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
        rows.append({"Year": i, "Revenue_mm": revenue, "EBITDA_mm": ebitda})
    return pd.DataFrame(rows)


def dcf_range(target: dict) -> dict:
    forecast = _dcf_forecast(target)

    def ufcf_row(row):
        da = row["Revenue_mm"] * target["DA_pctRevenue"]
        ebit = row["EBITDA_mm"] - da
        nopat = ebit * (1 - target["TaxRate"])
        capex = row["Revenue_mm"] * target["Capex_pctRevenue"]
        return nopat + da - capex  # NWC handled via balance deltas below

    forecast["UFCF_pre_nwc_mm"] = forecast.apply(ufcf_row, axis=1)
    forecast["NWC_balance_mm"] = forecast["Revenue_mm"] * target["NWC_pctRevenue"]
    prev_nwc = target["Revenue_LTM_mm"] * target["NWC_pctRevenue"]
    delta_nwc = []
    for bal in forecast["NWC_balance_mm"]:
        delta_nwc.append(bal - prev_nwc)
        prev_nwc = bal
    forecast["DeltaNWC_mm"] = delta_nwc
    forecast["UFCF_mm"] = forecast["UFCF_pre_nwc_mm"] - forecast["DeltaNWC_mm"]

    forecast.round(2).to_csv(os.path.join(OUTPUT_DIR, "dcf_forecast_detail.csv"), index=False)

    def ev_at(wacc):
        g = target["TerminalGrowthRate"]
        disc = [1 / (1 + wacc) ** y for y in forecast["Year"]]
        pv_fcf = sum(f * d for f, d in zip(forecast["UFCF_mm"], disc))
        tv = forecast["UFCF_mm"].iloc[-1] * (1 + g) / (wacc - g)
        return pv_fcf + tv * disc[-1]

    base_ev = ev_at(target["WACC"])
    ev_low = ev_at(target["WACC"] + 0.0075)
    ev_high = ev_at(target["WACC"] - 0.0075)

    return {"method": "DCF", "low": ev_low, "mid": base_ev, "high": ev_high}


# ---------------------------------------------------------------------------
# Method 4: LBO Ability-to-Pay
# ---------------------------------------------------------------------------

def _run_lbo_irr(target: dict, entry_multiple: float, exit_multiple: float) -> float:
    entry_ev = entry_multiple * target["EBITDA_LTM_mm"]
    fees = entry_ev * target["LBO_TransactionFeePct"]
    term_loan = target["LBO_TermLoanTurns"] * target["EBITDA_LTM_mm"]
    sub_notes = target["LBO_SubNotesTurns"] * target["EBITDA_LTM_mm"]
    total_debt = term_loan + sub_notes
    sponsor_equity = entry_ev + fees - total_debt

    if sponsor_equity <= 0:
        return float("inf")

    forecast = _dcf_forecast(target)
    tl_balance, sub_balance = term_loan, sub_notes
    tl_mandatory = term_loan * target["LBO_TermLoanMandatoryAmortPct"]
    prev_nwc = target["Revenue_LTM_mm"] * target["NWC_pctRevenue"]

    for _, row in forecast.iterrows():
        da = row["Revenue_mm"] * target["DA_pctRevenue"]
        ebit = row["EBITDA_mm"] - da
        interest = tl_balance * target["LBO_TermLoanRate"] + sub_balance * target["LBO_SubNotesRate"]
        ebt = ebit - interest
        taxes = max(ebt, 0) * target["TaxRate"]
        ni = ebt - taxes
        capex = row["Revenue_mm"] * target["Capex_pctRevenue"]
        nwc_bal = row["Revenue_mm"] * target["NWC_pctRevenue"]
        delta_nwc = nwc_bal - prev_nwc
        prev_nwc = nwc_bal
        fcf = ni + da - capex - delta_nwc

        mandatory = min(tl_mandatory, tl_balance)
        fcf_after_mandatory = max(fcf - mandatory, 0)
        sweep = fcf_after_mandatory * target["LBO_CashSweepPct"]
        tl_after_mandatory = tl_balance - mandatory
        sweep_to_tl = min(sweep, tl_after_mandatory)
        sweep_to_sub = min(sweep - sweep_to_tl, sub_balance)

        tl_balance = tl_after_mandatory - sweep_to_tl
        sub_balance = sub_balance - sweep_to_sub

    exit_ebitda = forecast["EBITDA_mm"].iloc[-1]
    exit_ev = exit_multiple * exit_ebitda
    exit_debt = tl_balance + sub_balance
    exit_equity = exit_ev - exit_debt

    if exit_equity <= 0:
        return -1.0

    moic = exit_equity / sponsor_equity
    irr = moic ** (1 / target["LBO_HoldPeriodYears"]) - 1
    return irr


def _solve_ability_to_pay(target: dict, target_irr: float) -> float:
    """Binary search for the entry (=exit) multiple that produces target_irr."""
    lo, hi = 3.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        irr = _run_lbo_irr(target, mid, mid)
        if irr > target_irr:
            lo = mid  # can afford to pay more
        else:
            hi = mid
    return (lo + hi) / 2


def lbo_ability_to_pay_range(target: dict) -> dict:
    base_multiple = _solve_ability_to_pay(target, target["LBO_TargetIRR"])
    aggressive_multiple = _solve_ability_to_pay(target, target["LBO_TargetIRR"] - 0.02)   # lower hurdle -> pay more
    conservative_multiple = _solve_ability_to_pay(target, target["LBO_TargetIRR"] + 0.02)  # higher hurdle -> pay less

    low = conservative_multiple * target["EBITDA_LTM_mm"]
    high = aggressive_multiple * target["EBITDA_LTM_mm"]
    mid = base_multiple * target["EBITDA_LTM_mm"]

    with open(os.path.join(OUTPUT_DIR, "lbo_ability_to_pay_detail.txt"), "w") as f:
        f.write(f"Target IRR hurdle: {target['LBO_TargetIRR']:.0%} -> max entry multiple {base_multiple:.2f}x "
                f"-> implied EV ${mid:,.1f}mm\n")
        f.write(f"Conservative sponsor ({target['LBO_TargetIRR']+0.02:.0%} hurdle): "
                f"max entry multiple {conservative_multiple:.2f}x -> implied EV ${low:,.1f}mm\n")
        f.write(f"Aggressive sponsor ({target['LBO_TargetIRR']-0.02:.0%} hurdle): "
                f"max entry multiple {aggressive_multiple:.2f}x -> implied EV ${high:,.1f}mm\n")

    return {"method": "LBO Ability-to-Pay", "low": low, "mid": mid, "high": high}


# ---------------------------------------------------------------------------
# Football field + recommendation
# ---------------------------------------------------------------------------

def plot_football_field(results: list, target_name: str):
    fig, ax = plt.subplots(figsize=(9, 4.5))
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
    lbo_res = lbo_ability_to_pay_range(target)

    results = [comps_res, prec_res, dcf_res, lbo_res]
    summary = pd.DataFrame(results)
    summary.round(1).to_csv(os.path.join(OUTPUT_DIR, "football_field_summary.csv"), index=False)

    plot_football_field(results, target["TargetName"])

    overall_low = min(r["low"] for r in results)
    overall_high = max(r["high"] for r in results)

    # Credible "core" range = overlap of DCF and Precedent Transactions (the two tightest,
    # most target-specific methods) - trading comps and LBO ability-to-pay are reported as
    # bracketing checks rather than folded into this overlap.
    dcf_low, dcf_high = dcf_res["low"], dcf_res["high"]
    prec_low, prec_high = prec_res["low"], prec_res["high"]
    core_low = max(dcf_low, prec_low)
    core_high = min(dcf_high, prec_high)
    lbo_high = lbo_res["high"]
    gap_to_lbo = core_low - lbo_high

    with open(os.path.join(OUTPUT_DIR, "recommendation.txt"), "w") as f:
        f.write(f"=== Valuation Summary: {target['TargetName']} ===\n\n")
        for r in results:
            f.write(f"{r['method']}: ${r['low']:,.0f}mm - ${r['high']:,.0f}mm (mid ${r['mid']:,.0f}mm)\n")
        f.write(f"\nFull range across all methods: ${overall_low:,.0f}mm - ${overall_high:,.0f}mm\n\n")
        f.write("=== Recommendation ===\n")
        f.write(
            f"Core recommended range (overlap of DCF and Precedent Transactions, the two most "
            f"target-specific methods): ${core_low:,.0f}mm - ${core_high:,.0f}mm. Trading comps "
            f"are treated as a sanity check rather than the primary anchor, since the public peer "
            f"set mixes an asset-light freight brokerage with asset-heavy carriers that trade at "
            f"structurally different multiples, widening that range well beyond the others.\n\n"
        )
        if gap_to_lbo > 0:
            f.write(
                f"Notably, the LBO ability-to-pay ceiling (${lbo_high:,.0f}mm) sits ${gap_to_lbo:,.0f}mm "
                f"below the bottom of the core range - a financial sponsor cannot underwrite synergies "
                f"the way a strategic acquirer can, so at this valuation level financial sponsors are "
                f"likely priced out of the process. Recommend running a targeted strategic-buyer process "
                f"rather than a broad auction that assumes sponsor participation at the core price.\n"
            )

    print(f"=== Pitch Book Valuation: {target['TargetName']} ===\n")
    for r in results:
        print(f"{r['method']:25s}  ${r['low']:>8,.0f}mm  -  ${r['high']:>8,.0f}mm   (mid ${r['mid']:,.0f}mm)")
    print(f"\nFull range: ${overall_low:,.0f}mm - ${overall_high:,.0f}mm")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
