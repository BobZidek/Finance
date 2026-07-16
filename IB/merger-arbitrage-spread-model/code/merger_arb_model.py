"""
Merger Arbitrage Spread Model - Vantage Pharma Solutions

Analyzes a pending all-cash acquisition from a merger-arbitrage
perspective: gross and annualized spread, the market-implied probability
of deal completion backed out from the current trading price, the
analyst's own expected return under an independently-assumed completion
probability, and the asymmetric risk/reward profile (small gain if the
deal closes vs. a much larger loss if it breaks).

Run:
    python merger_arb_model.py
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
        if k != "TargetName":
            a[k] = float(a[k])
    return a


def compute_spread_metrics(a: dict) -> dict:
    gross_spread = a["DealPrice"] - a["CurrentPrice"]
    gross_spread_pct = gross_spread / a["CurrentPrice"]
    annualized_spread_pct = gross_spread_pct * (365 / a["DaysToClose"])

    # Market-implied probability of close: solve CurrentPrice = P*DealPrice + (1-P)*Downside
    market_implied_prob = (a["CurrentPrice"] - a["DownsidePriceIfBroken"]) / \
        (a["DealPrice"] - a["DownsidePriceIfBroken"])

    downside_if_broken_pct = (a["CurrentPrice"] - a["DownsidePriceIfBroken"]) / a["CurrentPrice"]

    return {
        "gross_spread": gross_spread, "gross_spread_pct": gross_spread_pct,
        "annualized_spread_pct": annualized_spread_pct, "market_implied_prob": market_implied_prob,
        "downside_if_broken_pct": downside_if_broken_pct,
    }


def compute_expected_return(a: dict, probability: float) -> dict:
    expected_price = probability * a["DealPrice"] + (1 - probability) * a["DownsidePriceIfBroken"]
    expected_return_pct = (expected_price - a["CurrentPrice"]) / a["CurrentPrice"]
    annualized_expected_return = expected_return_pct * (365 / a["DaysToClose"])
    return {"expected_price": expected_price, "expected_return_pct": expected_return_pct,
            "annualized_expected_return": annualized_expected_return}


def probability_sensitivity(a: dict) -> pd.DataFrame:
    probs = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]
    rows = []
    for p in probs:
        res = compute_expected_return(a, p)
        rows.append({"AssumedProbability": p, "ExpectedPrice": res["expected_price"],
                     "ExpectedReturn_pct": res["expected_return_pct"] * 100,
                     "AnnualizedExpectedReturn_pct": res["annualized_expected_return"] * 100})
    return pd.DataFrame(rows)


def plot_probability_sensitivity(sens: pd.DataFrame, market_implied_prob: float, analyst_prob: float):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(sens["AssumedProbability"] * 100, sens["ExpectedReturn_pct"], marker="o", color="#2E5090")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(market_implied_prob * 100, color="#C0392B", linestyle="--",
               label=f"Market-Implied Probability ({market_implied_prob:.1%})")
    ax.axvline(analyst_prob * 100, color="#1E8449", linestyle="--",
               label=f"Analyst's Assumed Probability ({analyst_prob:.1%})")
    ax.set_xlabel("Assumed Probability of Deal Closing (%)")
    ax.set_ylabel("Expected Return to Close (%)")
    ax.set_title("Expected Return vs. Assumed Deal Completion Probability")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "probability_sensitivity.png"), dpi=150)
    plt.close(fig)


def plot_risk_reward(a: dict):
    fig, ax = plt.subplots(figsize=(7, 6))
    labels = ["If Deal Closes\n(upside)", "If Deal Breaks\n(downside)"]
    values = [a["DealPrice"] - a["CurrentPrice"], a["DownsidePriceIfBroken"] - a["CurrentPrice"]]
    colors = ["#1E8449", "#C0392B"]
    bars = ax.bar(labels, values, color=colors)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:+.2f}\n({h/a['CurrentPrice']:+.1%})", (bar.get_x() + bar.get_width() / 2, h),
                    ha="center", va="bottom" if h > 0 else "top")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("$ per Share")
    ax.set_title("Asymmetric Risk/Reward: Close vs. Break")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "risk_reward.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    spread = compute_spread_metrics(a)
    analyst_view = compute_expected_return(a, a["AnalystProbabilityOfClose"])
    sens = probability_sensitivity(a)
    sens.round(2).to_csv(os.path.join(OUTPUT_DIR, "probability_sensitivity.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "merger_arb_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write(f"Deal Price: ${a['DealPrice']:.2f}  |  Current Price: ${a['CurrentPrice']:.2f}  |  "
                f"Pre-Announcement Price: ${a['PreAnnouncementPrice']:.2f}\n")
        f.write(f"Downside Price if Deal Breaks: ${a['DownsidePriceIfBroken']:.2f}\n")
        f.write(f"Days to Close: {a['DaysToClose']:.0f}\n\n")
        f.write(f"Gross Spread: ${spread['gross_spread']:.2f} ({spread['gross_spread_pct']:.2%})\n")
        f.write(f"Annualized Spread (assuming certain close): {spread['annualized_spread_pct']:.2%}\n")
        f.write(f"Downside if Deal Breaks: {spread['downside_if_broken_pct']:.2%}\n\n")
        f.write(f"Market-Implied Probability of Close: {spread['market_implied_prob']:.2%}\n")
        f.write(f"  (Note: this is, by construction, also the breakeven probability - the current "
                f"price already reflects zero expected return at exactly this probability.)\n\n")
        f.write(f"=== Analyst's View (assumed {a['AnalystProbabilityOfClose']:.0%} probability of close) ===\n")
        f.write(f"Expected Price: ${analyst_view['expected_price']:.2f}\n")
        f.write(f"Expected Return to Close: {analyst_view['expected_return_pct']:.2%}\n")
        f.write(f"Annualized Expected Return: {analyst_view['annualized_expected_return']:.2%}\n\n")
        f.write("=== Probability Sensitivity ===\n")
        f.write(sens.round(2).to_string(index=False))

    plot_probability_sensitivity(sens, spread["market_implied_prob"], a["AnalystProbabilityOfClose"])
    plot_risk_reward(a)

    print(f"=== Merger Arbitrage: {a['TargetName']} ===")
    print(f"Gross Spread: ${spread['gross_spread']:.2f} ({spread['gross_spread_pct']:.2%})  |  "
          f"Annualized: {spread['annualized_spread_pct']:.2%}")
    print(f"Market-Implied Probability of Close: {spread['market_implied_prob']:.2%}")
    print(f"\nAnalyst's Assumed Probability: {a['AnalystProbabilityOfClose']:.0%}")
    print(f"Expected Return to Close: {analyst_view['expected_return_pct']:.2%}  "
          f"(Annualized: {analyst_view['annualized_expected_return']:.2%})")
    print(f"\nDownside if deal breaks: {spread['downside_if_broken_pct']:.2%} vs. "
          f"upside if closes: {spread['gross_spread_pct']:.2%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
