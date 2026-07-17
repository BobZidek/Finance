# IPO Valuation & Readiness — Theory

## Why IPO pricing is deliberately NOT set at "fair value"

Every other valuation project in this repo tries to estimate a company's *true* intrinsic
value. IPO pricing does something subtly different: underwriters typically price the offering
**below** their own comps-implied intrinsic estimate — this project prices at **$18.00 against
a $20.00 comps-implied midpoint, a 10% discount** — a well-documented, deliberate industry
practice, not an error or a negotiating loss for the company.

## Why underpricing is standard practice

1. **Aftermarket demand ("the pop")**: a stock that opens for public trading and immediately
   rises above its offer price generates strong press coverage, investor goodwill, and
   demonstrates strong demand — all of which matter for the company's ability to raise capital
   again later (secondary offerings, follow-on raises) and for employee/insider sentiment
   around their now-public equity.
2. **Compensating IPO investors for uncertainty**: investors buying in an IPO take on
   information asymmetry risk (the company and its bankers know more about the business than
   public investors do) and liquidity risk (no trading history yet) — a discount compensates
   for that risk, similar in spirit to the illiquidity discount concept elsewhere in private
   valuation work.
3. **Building a durable relationship with anchor investors**: underwriters allocate IPO shares
   to large institutional investors who are expected to be long-term holders; leaving room for
   a reasonable first-day gain helps cultivate that relationship for future deals.

## Quantifying the cost of underpricing: "money left on the table"

```
Money Left on the Table = (Intrinsic Value per Share - Offer Price) x Total Shares Sold
```

This project's IPO leaves **$34.5mm on the table** — the gap between what the shares could
plausibly have been priced at (the comps-implied intrinsic midpoint) and what they were
actually sold for, multiplied by all shares actually sold in the offering (primary + secondary
+ greenshoe). This is a **real, quantifiable cost** borne by the company (which raised less
primary capital than it "could have") and the selling shareholders (who received less for their
secondary shares) — the standard trade-off analysis behind every IPO pricing decision, and
exactly why "how much should we discount" is a genuinely debated question between the company
and its underwriters.

## Primary vs. secondary shares — a critical distinction

- **Primary shares**: newly issued shares. Proceeds go to the **company** (net of underwriting
  fees), used for growth capital, debt paydown, or general corporate purposes.
- **Secondary shares**: existing shares sold by current holders (often early VCs or employees).
  Proceeds go to **those sellers**, not the company — secondary shares raise no new capital for
  the business at all, they simply provide liquidity to pre-IPO holders.

This project's structure (12mm primary, 3mm secondary, 80% of the base offering being primary)
is typical for a growth-stage tech IPO still prioritizing capital raising over insider liquidity
— a more mature company further from needing growth capital might structure the reverse mix.

## The greenshoe (over-allotment option)

Underwriters typically have the right to sell up to **15% more shares than the base offering**
(this project models exactly 15%) if demand is strong — usually satisfied either by borrowing
shares from the company (increasing dilution, as modeled here) or by the underwriters'
short-covering in the aftermarket (which doesn't dilute existing holders, since it doesn't
involve new share issuance). This project assumes the more dilutive (all-primary) treatment for
simplicity — see `ENHANCEMENTS.md` for modeling the alternative.

## Dilution and public float

```
Existing Holder Ownership (post-IPO) = Pre-IPO Shares / Post-IPO Total Shares
Public Float % = Shares Actually Sold in the Offering / Post-IPO Total Shares
```

This project's IPO dilutes existing holders from 100% (pre-IPO) to **89.3%** — a real but
modest dilution from a single primary issuance of ~12% of the company. The resulting **13.0%
public float** is deliberately low relative to full ownership — common for tech IPOs, which
often keep float tight initially (partly to support price stability, partly because most
pre-IPO holders remain subject to a post-IPO lock-up period before they can sell).
