# GP-Led Continuation Funds — Theory

## What a continuation fund is, and why they've become so common

A traditional PE fund has a fixed life (typically ~10 years) and must eventually sell every
portfolio company and return capital to LPs. But sometimes a GP's **best-performing** asset
still has significant value creation runway left when the fund's life is ending — selling it
to a third party purely because the fund's clock ran out can leave real value on the table. A
**GP-led continuation fund** transaction solves this: the GP moves the asset (or a small
group of assets) into a **newly-formed vehicle**, at an independently negotiated Net Asset
Value (NAV), and gives the **existing LPs a choice**:

1. **Roll** their interest into the new continuation vehicle, continuing to hold economic
   exposure to the asset, or
2. **Cash out** at the transaction NAV, with new **secondary investors** supplying the capital
   to buy them out.

This structure has grown enormously in the 2020s specifically because it lets high-conviction
GPs hold onto their best assets longer while still honoring the original fund's obligation to
return capital to LPs who want liquidity now.

## The genuine conflict of interest at the center of every continuation deal

The GP is simultaneously the **seller** (representing the old fund, whose LPs it has a
fiduciary duty to) and, functionally, the **buyer** (sponsoring and managing the new
continuation vehicle, which will pay it fresh carried interest going forward). This structural
conflict is exactly why real GP-led transactions require an **independent fairness opinion** on
the transaction NAV and, typically, sign-off from the fund's **LP Advisory Committee (LPAC)** —
safeguards specifically designed to counter the GP's incentive to set a favorable-to-itself
transaction price.

## Step 1: carry crystallizes on the old fund's gain

```
Old Fund Gain = Transaction NAV − Old Fund Cost Basis
GP Carry (crystallized) = Old Fund Gain x Carry %
Net LP Proceeds at Transaction = Transaction NAV − GP Carry
```

In this project: **$450mm NAV against a $120mm original cost basis produces a $330mm gain**,
crystallizing **$66mm of GP carry immediately** — the same mechanical carry calculation used
throughout the [`PE/fund-model-waterfall`](../fund-model-waterfall) project, just triggered by
a continuation transaction instead of a traditional third-party sale.

## Step 2: the new fund starts a fresh basis — and a fresh carry clock

```
New Fund Cost Basis = Net LP Proceeds at Transaction (split between rolling LPs and new
                        secondary investors, each buying in at the same $/NAV basis)
```

The **new fund's cost basis is the post-carry NAV**, not the old fund's original cost basis.
This means when the continuation vehicle eventually exits, **any gain above this new (higher)
basis triggers a SECOND round of GP carry** — even though a substantial portion of the
company's total value creation (everything up to the transaction NAV) already had carry taken
on it once.

## Quantifying the "double-dip" — the real critique of continuation funds

This project runs the numbers both ways on the exact same final outcome ($650mm exit, 4 years
after the transaction):

| Structure | Total GP Carry |
|---|---|
| **Two-step (continuation transaction + eventual exit)** | **$119.2mm** |
| **Single continuous fund** (same $120mm original basis, same $650mm final exit, one crystallization) | $106.0mm |
| **Difference** | **+$13.2mm (+12.5%)** |

**The continuation structure produces 12.5% more total carry for the GP than a single
continuous fund holding the same asset to the same final outcome would have** — purely from
crystallizing carry twice on overlapping value creation, not from the GP delivering any
additional actual return to investors. This is the precise, quantified version of the
"double-dip" criticism leveled at continuation fund structures — and exactly why LPACs,
independent valuations, and increasingly standardized market practice (status-quo options,
extended election periods, third-party price validation) have become essential features of a
well-governed GP-led transaction, not optional extras.

## What rolling LPs and new secondary investors actually get

Both groups in this project earn the **same MOIC (1.554x) and IRR (11.7%)** from the
transaction date to the eventual exit — a direct consequence of both investing in the
continuation fund at the **same $/NAV basis** and sharing pro-rata in the same subsequent gain.
This is exactly how it should work in a fairly-priced transaction: **neither the rolling LPs
nor the new secondary buyers should be structurally advantaged over the other by the pricing
itself** — any difference in realized outcome should come from a real difference in risk
tolerance or investment horizon, not from the transaction terms unfairly favoring one side.
