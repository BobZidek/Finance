"""
Dividend Recapitalization & Credit Analysis - Crestline Media Networks

Models a mid-hold leveraged dividend recapitalization for a PE-owned
portfolio company: pre/post-recap credit metrics (leverage, interest
coverage) mapped to an approximate credit rating band via a simplified
scorecard, and a sponsor IRR/MOIC comparison between the "with recap"
and "without recap" (counterfactual) paths to the same exit.

Run:
    python dividend_recap_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "recap_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    a["RecapYear"] = int(a["RecapYear"])
    a["ExitYear"] = int(a["ExitYear"])
    return a


def blended_rate(existing_debt, existing_rate, new_debt, new_rate):
    total = existing_debt + new_debt
    return (existing_debt * existing_rate + new_debt * new_rate) / total if total > 0 else 0.0


def credit_rating_band(leverage: float, coverage: float) -> str:
    """Simplified scorecard, conservative 'weakest link' approach - the worse
    of the two metrics determines the band, consistent with how rating
    agencies weight leverage and coverage as the primary credit drivers."""
    if leverage < 3.0 and coverage > 5.0:
        return "BB+/BB"
    elif leverage < 4.0 and coverage > 3.5:
        return "BB-/B+"
    elif leverage < 5.0 and coverage > 2.5:
        return "B+/B"
    elif leverage < 6.0 and coverage > 1.5:
        return "B-/CCC+"
    else:
        return "CCC or below"


def credit_metrics(debt, ebitda, rate) -> dict:
    interest = debt * rate
    leverage = debt / ebitda
    coverage = ebitda / interest if interest > 0 else float("inf")
    rating = credit_rating_band(leverage, coverage)
    return {"Debt_mm": debt, "EBITDA_mm": ebitda, "Interest_mm": interest,
            "Leverage_x": leverage, "Coverage_x": coverage, "ImpliedRating": rating}


def project_debt_paydown(start_debt, start_year, end_year, ebitda_year_start, growth_rate,
                          fcf_conversion_pct, interest_rate) -> list:
    """Paydown capacity is FCF-based (EBITDA x conversion% MINUS interest expense on the
    beginning-of-year balance), not a flat % of EBITDA - so a higher debt load (and its
    higher interest burden) genuinely slows deleveraging, rather than paying down at an
    identical dollar pace regardless of capital structure."""
    rows = []
    debt = start_debt
    ebitda = ebitda_year_start
    for year in range(start_year + 1, end_year + 1):
        ebitda = ebitda * (1 + growth_rate)
        interest_expense = debt * interest_rate
        fcf_available = max(fcf_conversion_pct * ebitda - interest_expense, 0)
        paydown = min(fcf_available, debt)
        debt -= paydown
        rows.append({"Year": year, "EBITDA_mm": ebitda, "InterestExpense_mm": interest_expense, "Debt_mm": debt})
    return rows


def compute_irr(cashflows: list, guess_lo=-0.99, guess_hi=5.0, tol=1e-6, max_iter=200) -> float:
    def npv(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))

    lo, hi = guess_lo, guess_hi
    if npv(lo) * npv(hi) > 0:
        return float("nan")
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        if abs(npv(mid)) < tol:
            return mid
        if npv(lo) * npv(mid) < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    pre_recap = credit_metrics(a["PreRecap_Debt_mm"], a["PreRecap_EBITDA_mm"], a["PreRecap_BlendedRate"])

    post_recap_debt = a["PreRecap_Debt_mm"] + a["NewDebtRaised_mm"]
    post_recap_rate = blended_rate(a["PreRecap_Debt_mm"], a["PreRecap_BlendedRate"],
                                     a["NewDebtRaised_mm"], a["NewTrancheRate"])
    post_recap = credit_metrics(post_recap_debt, a["PreRecap_EBITDA_mm"], post_recap_rate)

    credit_df = pd.DataFrame([
        {"Scenario": "Pre-Recap", **pre_recap},
        {"Scenario": "Post-Recap", **post_recap},
    ])
    credit_df.round(3).to_csv(os.path.join(OUTPUT_DIR, "credit_metrics.csv"), index=False)

    # With-recap path: debt jumps at recap year, then pays down to exit (paydown capacity
    # reduced by the new tranche's higher blended interest rate)
    with_recap_schedule = project_debt_paydown(post_recap_debt, a["RecapYear"], a["ExitYear"],
                                                 a["PreRecap_EBITDA_mm"], a["EBITDAGrowthRate"],
                                                 a["FCFConversionPctEBITDA"], post_recap_rate)
    with_recap_df = pd.DataFrame(with_recap_schedule)
    exit_ebitda_with = with_recap_df["EBITDA_mm"].iloc[-1]
    exit_debt_with = with_recap_df["Debt_mm"].iloc[-1]
    exit_ev_with = a["ExitMultiple"] * exit_ebitda_with
    exit_equity_with = exit_ev_with - exit_debt_with

    # Without-recap counterfactual: no new debt, same FCF conversion but only the original
    # (lower) pre-recap blended rate applies - deleverages faster with no recap
    without_recap_schedule = project_debt_paydown(a["PreRecap_Debt_mm"], a["RecapYear"], a["ExitYear"],
                                                    a["PreRecap_EBITDA_mm"], a["EBITDAGrowthRate"],
                                                    a["FCFConversionPctEBITDA"], a["PreRecap_BlendedRate"])
    without_recap_df = pd.DataFrame(without_recap_schedule)
    exit_ebitda_without = without_recap_df["EBITDA_mm"].iloc[-1]
    exit_debt_without = without_recap_df["Debt_mm"].iloc[-1]
    exit_ev_without = a["ExitMultiple"] * exit_ebitda_without
    exit_equity_without = exit_ev_without - exit_debt_without

    # Sponsor cash flow series (Year 0 entry, recap year dividend if applicable, exit year proceeds)
    cf_with = [0.0] * (a["ExitYear"] + 1)
    cf_with[0] = -a["SponsorEntryEquity_mm"]
    cf_with[a["RecapYear"]] += a["DividendPaid_mm"]
    cf_with[a["ExitYear"]] += exit_equity_with
    irr_with = compute_irr(cf_with)
    moic_with = (a["DividendPaid_mm"] + exit_equity_with) / a["SponsorEntryEquity_mm"]

    cf_without = [0.0] * (a["ExitYear"] + 1)
    cf_without[0] = -a["SponsorEntryEquity_mm"]
    cf_without[a["ExitYear"]] += exit_equity_without
    irr_without = compute_irr(cf_without)
    moic_without = exit_equity_without / a["SponsorEntryEquity_mm"]

    returns_df = pd.DataFrame([
        {"Scenario": "With Dividend Recap", "InterimDividend_mm": a["DividendPaid_mm"],
         "ExitEquity_mm": exit_equity_with, "TotalProceeds_mm": a["DividendPaid_mm"] + exit_equity_with,
         "MOIC": moic_with, "IRR": irr_with * 100},
        {"Scenario": "Without Recap (counterfactual)", "InterimDividend_mm": 0.0,
         "ExitEquity_mm": exit_equity_without, "TotalProceeds_mm": exit_equity_without,
         "MOIC": moic_without, "IRR": irr_without * 100},
    ])
    returns_df.round(2).to_csv(os.path.join(OUTPUT_DIR, "sponsor_returns_comparison.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "recap_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write("=== Credit Metrics: Pre- vs. Post-Recap ===\n")
        f.write(credit_df.round(3).to_string(index=False))
        f.write(f"\n\nNew debt raised: ${a['NewDebtRaised_mm']:,.0f}mm @ {a['NewTrancheRate']:.1%}\n")
        f.write(f"Dividend paid to sponsor: ${a['DividendPaid_mm']:,.0f}mm\n\n")
        f.write("=== Sponsor Returns: With vs. Without Recap ===\n")
        f.write(returns_df.round(2).to_string(index=False))
        f.write(f"\n\nIRR impact of the recap: {(irr_with - irr_without) * 100:+.1f} percentage points\n")
        f.write(f"MOIC impact of the recap: {(moic_with - moic_without):+.2f}x\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["Leverage_x", "Coverage_x"]
    x = range(len(metrics))
    width = 0.35
    ax.bar([i - width / 2 for i in x], [pre_recap[m] for m in metrics], width, label="Pre-Recap", color="#1E8449")
    ax.bar([i + width / 2 for i in x], [post_recap[m] for m in metrics], width, label="Post-Recap", color="#C0392B")
    ax.set_xticks(list(x))
    ax.set_xticklabels(["Leverage (Debt/EBITDA)", "Coverage (EBITDA/Interest)"])
    ax.set_title(f"Credit Metrics: Pre- vs. Post-Recap\n"
                 f"{pre_recap['ImpliedRating']} -> {post_recap['ImpliedRating']}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "credit_metrics.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(returns_df["Scenario"], returns_df["IRR"], color=["#2E5090", "#7FA6D9"])
    for bar, moic in zip(bars, returns_df["MOIC"]):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}% IRR\n{moic:.2f}x MOIC", (bar.get_x() + bar.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("IRR (%)")
    ax.set_title("Sponsor Returns: With vs. Without Dividend Recap")
    plt.xticks(rotation=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "returns_comparison.png"), dpi=150)
    plt.close(fig)

    print(f"=== Dividend Recap & Credit Analysis: {a['CompanyName']} ===")
    print(credit_df.round(3).to_string(index=False))
    print(f"\nCredit rating impact: {pre_recap['ImpliedRating']} -> {post_recap['ImpliedRating']}\n")
    print(returns_df.round(2).to_string(index=False))
    print(f"\nIRR impact: {(irr_with - irr_without) * 100:+.1f}pp  |  MOIC impact: {(moic_with - moic_without):+.2f}x")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
