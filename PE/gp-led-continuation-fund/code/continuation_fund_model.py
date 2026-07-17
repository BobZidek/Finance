"""
GP-Led Continuation Fund Transaction - Crestpoint Industrial Services

Models a single-asset GP-led secondary transaction: an aging fund's sole
remaining portfolio company is moved into a new continuation vehicle at
an independently negotiated NAV. Existing LPs choose to roll their
interest into the new vehicle or cash out (bought out by new secondary
investors), and the GP crystallizes carry on the OLD fund's gain at the
transaction - then can earn carry AGAIN on the NEW fund's subsequent
gain at the eventual exit. This project quantifies exactly how much
additional total carry that two-step crystallization produces versus a
single continuous fund holding to the same final outcome - the core of
the real "double-dip" critique of continuation fund structures.

Run:
    python continuation_fund_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "transaction_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    a["ExitYearsFromTransaction"] = int(a["ExitYearsFromTransaction"])
    return a


def run_transaction(a: dict) -> dict:
    old_fund_gain = a["TransactionNAV_mm"] - a["OldFundCostBasis_mm"]
    old_fund_carry = old_fund_gain * a["CarryPct"]
    net_lp_proceeds_at_transaction = a["TransactionNAV_mm"] - old_fund_carry

    rolling_amount = net_lp_proceeds_at_transaction * a["RollingLPPct"]
    cashout_amount = net_lp_proceeds_at_transaction * (1 - a["RollingLPPct"])

    new_fund_cost_basis = rolling_amount + cashout_amount  # == net_lp_proceeds_at_transaction, by construction
    rolling_lp_new_ownership_pct = rolling_amount / new_fund_cost_basis
    secondary_investor_ownership_pct = cashout_amount / new_fund_cost_basis

    return {
        "old_fund_gain": old_fund_gain, "old_fund_carry": old_fund_carry,
        "net_lp_proceeds_at_transaction": net_lp_proceeds_at_transaction,
        "rolling_amount": rolling_amount, "cashout_amount": cashout_amount,
        "new_fund_cost_basis": new_fund_cost_basis,
        "rolling_lp_ownership_pct": rolling_lp_new_ownership_pct,
        "secondary_investor_ownership_pct": secondary_investor_ownership_pct,
    }


def run_new_fund_exit(a: dict, txn: dict) -> dict:
    new_fund_gain = a["FutureExitValue_mm"] - txn["new_fund_cost_basis"]
    new_fund_carry = new_fund_gain * a["CarryPct"]
    net_proceeds_at_exit = a["FutureExitValue_mm"] - new_fund_carry

    rolling_lp_proceeds = net_proceeds_at_exit * txn["rolling_lp_ownership_pct"]
    secondary_investor_proceeds = net_proceeds_at_exit * txn["secondary_investor_ownership_pct"]

    rolling_lp_moic = rolling_lp_proceeds / txn["rolling_amount"]
    rolling_lp_irr = rolling_lp_moic ** (1 / a["ExitYearsFromTransaction"]) - 1
    secondary_moic = secondary_investor_proceeds / txn["cashout_amount"]
    secondary_irr = secondary_moic ** (1 / a["ExitYearsFromTransaction"]) - 1

    return {
        "new_fund_gain": new_fund_gain, "new_fund_carry": new_fund_carry,
        "net_proceeds_at_exit": net_proceeds_at_exit,
        "rolling_lp_proceeds": rolling_lp_proceeds, "secondary_investor_proceeds": secondary_investor_proceeds,
        "rolling_lp_moic": rolling_lp_moic, "rolling_lp_irr": rolling_lp_irr,
        "secondary_moic": secondary_moic, "secondary_irr": secondary_irr,
    }


def compare_to_single_continuous_fund(a: dict, total_carry_two_step: float) -> dict:
    single_fund_gain = a["FutureExitValue_mm"] - a["OldFundCostBasis_mm"]
    single_fund_carry = single_fund_gain * a["CarryPct"]
    carry_difference = total_carry_two_step - single_fund_carry
    return {"single_fund_gain": single_fund_gain, "single_fund_carry": single_fund_carry,
            "carry_difference": carry_difference,
            "carry_increase_pct": carry_difference / single_fund_carry}


def plot_carry_comparison(txn: dict, exit_res: dict, comparison: dict):
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["Old Fund Carry\n(at transaction)", "New Fund Carry\n(at exit)", "Total\n(Two-Step)",
              "Single Continuous\nFund Carry"]
    values = [txn["old_fund_carry"], exit_res["new_fund_carry"],
              txn["old_fund_carry"] + exit_res["new_fund_carry"], comparison["single_fund_carry"]]
    colors = ["#7FA6D9", "#7FA6D9", "#C0392B", "#1E8449"]
    bars = ax.bar(labels, values, color=colors)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:,.1f}mm", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("GP Carry ($mm)")
    ax.set_title(f"GP Carry: Two-Step Continuation vs. Single Continuous Fund\n"
                 f"(+${comparison['carry_difference']:,.1f}mm, {comparison['carry_increase_pct']:+.1%})")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "carry_comparison.png"), dpi=150)
    plt.close(fig)


def plot_lp_outcomes(txn: dict, exit_res: dict):
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["Rolling LPs", "Secondary Investors"]
    invested = [txn["rolling_amount"], txn["cashout_amount"]]
    proceeds = [exit_res["rolling_lp_proceeds"], exit_res["secondary_investor_proceeds"]]
    x = range(len(labels))
    width = 0.35
    ax.bar([i - width / 2 for i in x], invested, width, label="Invested (at transaction)", color="#7FA6D9")
    ax.bar([i + width / 2 for i in x], proceeds, width, label="Proceeds (at exit)", color="#1E8449")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("$mm")
    ax.set_title("Continuation Fund Investor Outcomes")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "lp_outcomes.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    txn = run_transaction(a)
    exit_res = run_new_fund_exit(a, txn)
    total_carry_two_step = txn["old_fund_carry"] + exit_res["new_fund_carry"]
    comparison = compare_to_single_continuous_fund(a, total_carry_two_step)

    plot_carry_comparison(txn, exit_res, comparison)
    plot_lp_outcomes(txn, exit_res)

    with open(os.path.join(OUTPUT_DIR, "continuation_fund_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write("=== Step 1: GP-Led Continuation Transaction ===\n")
        f.write(f"Old Fund Cost Basis: ${a['OldFundCostBasis_mm']:,.1f}mm\n")
        f.write(f"Transaction NAV: ${a['TransactionNAV_mm']:,.1f}mm\n")
        f.write(f"Old Fund Gain: ${txn['old_fund_gain']:,.1f}mm\n")
        f.write(f"GP Carry Crystallized (Old Fund, {a['CarryPct']:.0%}): ${txn['old_fund_carry']:,.1f}mm\n")
        f.write(f"Net LP Proceeds at Transaction: ${txn['net_lp_proceeds_at_transaction']:,.1f}mm\n\n")
        f.write(f"Rolling LPs ({a['RollingLPPct']:.0%}): ${txn['rolling_amount']:,.1f}mm rolled into new fund\n")
        f.write(f"Cash-Out LPs ({1-a['RollingLPPct']:.0%}): ${txn['cashout_amount']:,.1f}mm paid by new "
                f"secondary investors\n")
        f.write(f"New Continuation Fund Cost Basis: ${txn['new_fund_cost_basis']:,.1f}mm\n\n")
        f.write(f"=== Step 2: Continuation Fund Exit ({a['ExitYearsFromTransaction']:.0f} years later) ===\n")
        f.write(f"Exit Value: ${a['FutureExitValue_mm']:,.1f}mm\n")
        f.write(f"New Fund Gain: ${exit_res['new_fund_gain']:,.1f}mm\n")
        f.write(f"GP Carry Crystallized (New Fund): ${exit_res['new_fund_carry']:,.1f}mm\n\n")
        f.write(f"Rolling LPs: ${txn['rolling_amount']:,.1f}mm -> ${exit_res['rolling_lp_proceeds']:,.1f}mm  "
                f"(MOIC {exit_res['rolling_lp_moic']:.3f}x, IRR {exit_res['rolling_lp_irr']:.1%})\n")
        f.write(f"Secondary Investors: ${txn['cashout_amount']:,.1f}mm -> "
                f"${exit_res['secondary_investor_proceeds']:,.1f}mm  "
                f"(MOIC {exit_res['secondary_moic']:.3f}x, IRR {exit_res['secondary_irr']:.1%})\n\n")
        f.write("=== The 'Double-Dip' Comparison ===\n")
        f.write(f"Total GP Carry (two-step: transaction + eventual exit): ${total_carry_two_step:,.1f}mm\n")
        f.write(f"GP Carry under a SINGLE continuous fund (same final outcome, one crystallization event): "
                f"${comparison['single_fund_carry']:,.1f}mm\n")
        f.write(f"Additional Carry from the Continuation Structure: ${comparison['carry_difference']:,.1f}mm "
                f"({comparison['carry_increase_pct']:+.1%})\n")

    print(f"=== GP-Led Continuation Fund: {a['CompanyName']} ===")
    print(f"Old Fund Carry Crystallized: ${txn['old_fund_carry']:,.1f}mm")
    print(f"New Fund Carry at Exit: ${exit_res['new_fund_carry']:,.1f}mm")
    print(f"Total Two-Step Carry: ${total_carry_two_step:,.1f}mm")
    print(f"\nvs. Single Continuous Fund Carry: ${comparison['single_fund_carry']:,.1f}mm")
    print(f"Additional Carry from Continuation Structure: ${comparison['carry_difference']:,.1f}mm "
          f"({comparison['carry_increase_pct']:+.1%})\n")
    print(f"Rolling LP: MOIC {exit_res['rolling_lp_moic']:.3f}x, IRR {exit_res['rolling_lp_irr']:.1%}")
    print(f"Secondary Investor: MOIC {exit_res['secondary_moic']:.3f}x, IRR {exit_res['secondary_irr']:.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
