# Distressed Debt Recovery & the Fulcrum Security — Theory

## Absolute priority — the rule that governs everything here

In a Chapter 11 reorganization, distributable value flows to claimants in **strict seniority
order** — the **absolute priority rule** — meaning a junior class receives **nothing** until
every class senior to it is paid in full (in practice, negotiated settlements and "gifting"
sometimes deviate from strict priority, but strict priority is the legal default and the
correct analytical starting point). This project distributes an assumed reorganization
enterprise value down the capital structure exactly this way:

```
For each tranche, in seniority order:
    Recovery = min(Remaining Value, Tranche's Par Claim)
    Remaining Value -= Recovery
```

Secured claims (the ABL Revolver and First Lien Term Loan here) are paid before unsecured
claims of the same tier, and within each tier, more senior instruments are paid before more
junior ones — exactly mirroring real capital structure seniority.

## The fulcrum security — the single most important concept in distressed investing

The **fulcrum security** is the specific tranche where recoverable value **runs out mid-claim**
— it's the class that receives a **partial** recovery, sitting exactly at the boundary between
"fully recovers" (everything senior) and "recovers nothing" (everything junior). This project's
base case identifies **Second Lien Notes** as the fulcrum security: the ABL Revolver and First
Lien Term Loan recover 100% ($80mm and $320mm respectively), Second Lien recovers only 36.7%
($55mm of its $150mm claim), and everything junior (Senior Unsecured Notes, Subordinated Notes,
and Common Equity) recovers nothing.

**Why this matters more than any other single fact in a distressed situation**: in a real
restructuring, the fulcrum security's holders are the ones who typically **receive the new
equity of the reorganized company** (via a debt-for-equity conversion), because they're the
class whose claim value is genuinely uncertain and tied to the company's actual go-forward
value — everyone senior gets made whole in cash or new debt, everyone junior gets wiped out.
**This means the fulcrum security's holders are the true economic owners of the post-
reorganization company, not the pre-petition common equity holders.** Distressed debt
investors specifically target buying fulcrum securities (often at a steep discount from
distressed sellers) precisely to gain control of the reorganized company's equity.

## Reading the sensitivity chart

`output/recovery_by_ev.png` sweeps reorganization enterprise value from $300mm to $900mm and
plots every tranche's recovery % across that range — showing exactly **which tranche is the
fulcrum security at any given valuation outcome**, not just the base case. This matters because
reorganization enterprise value estimates are inherently uncertain (they typically come from
the same comps/DCF methodologies used elsewhere in this repo, applied to a company in
distress, where forecasting is especially hard) — a distressed investor needs to understand how
the fulcrum shifts across the plausible valuation range, not just at one point estimate. In
this project's sensitivity, the fulcrum shifts from the First Lien Term Loan (at low EVs, where
even secured debt is impaired) up through Second Lien and eventually to Senior Unsecured Notes
as reorganization value rises — a single security can be "the fulcrum" at one valuation and
comfortably money-good or completely wiped out at others.

## Why "impairment" doesn't mean "worthless"

The base case shows **total funded debt ($850mm) recovering only $455mm in aggregate — a
46.5% overall impairment** — but that headline number obscures enormous dispersion: senior
secured claims are made completely whole while junior unsecured claims are wiped out entirely.
This is exactly why distressed investors analyze the **capital structure waterfall**, not just
an aggregate "how impaired is this company" number — the *specific tranche* an investor owns
(or is considering buying) determines their actual outcome far more than the company's overall
distress level does.
