# Asset-Based Lending & the Borrowing Base — Theory

## A fundamentally different lending philosophy

Every debt instrument elsewhere in this repo (Term Loans, Subordinated Notes, high-yield bonds)
is sized as a **multiple of EBITDA** — the lender is underwriting the borrower's cash flow
generation. **Asset-based lending (ABL)** works completely differently: the facility is sized
as a **percentage of specific, identifiable collateral** — primarily accounts receivable and
inventory — updated regularly (often weekly or monthly) as that collateral changes. This makes
ABL the natural financing tool for working-capital-intensive, often lower-margin or more
cyclical businesses (distributors, retailers, manufacturers) where cash flow can be volatile
but the underlying receivables and inventory provide tangible, monitorable collateral value —
exactly the profile of this project's hypothetical industrial distributor.

## Building the borrowing base, component by component

### Accounts Receivable

```
Eligible AR = Gross AR − Ineligible AR (>90 days past due, customer concentration
              limits, foreign/contra accounts, disputed invoices)
AR Component = Eligible AR x AR Advance Rate (typically 80-85%)
```

The advance rate (85% here) reflects the lender's own estimate of collection risk — even
"eligible" receivables aren't advanced against at 100%, since some fraction will always prove
uncollectible or disputed.

### Inventory — a second layer of conservatism

```
Eligible Inventory (at cost) = Gross Inventory − Ineligible Inventory (obsolete, slow-moving)
Eligible Inventory (at NOLV) = Eligible Inventory (at cost) x NOLV %
Inventory Component = Eligible Inventory (at NOLV) x Inventory Advance Rate (typically 50-65%)
```

Inventory gets **two** haircuts, not one. First, a third-party appraiser estimates **Net
Orderly Liquidation Value (NOLV)** — what the inventory could realistically fetch in an
orderly (not fire-sale) liquidation, which is almost always well below cost (72% here) since
inventory rarely sells for what it cost to produce or acquire once a lender actually needs to
liquidate it. Only *then* does the (typically lower) inventory advance rate apply on top —
reflecting that inventory is fundamentally less certain collateral than receivables (subject to
obsolescence, damage, and market price risk that AR doesn't carry).

## Availability: the lesser of two numbers

```
Availability = MIN(Net Borrowing Base, Facility Commitment)
```

The **facility commitment** ($75mm here) is the maximum the lender has contractually agreed to
lend — but it's frequently sized **larger** than the current borrowing base allows, anticipating
future growth in the collateral base. **The actual binding constraint today is whichever number
is smaller** — in this project, the $57.82mm borrowing base, not the $75mm facility ceiling.

## Excess Availability and the springing covenant

```
Excess Availability = Availability − Outstanding Draws − Letters of Credit
```

**Excess Availability is the single most important number a borrower and lender both watch
day to day** — it's the borrower's actual undrawn liquidity cushion. Many ABL facilities carry
a **springing financial covenant**: standard maintenance covenants (like a fixed charge
coverage ratio test) only "spring" into effect — become testable — once Excess Availability
falls **below** a specified threshold (here, 10% of the facility commitment, $7.5mm). This
project's base case shows **$22.82mm of Excess Availability, comfortably above the $7.5mm
threshold** — the covenant isn't currently being tested at all, a real and meaningful
distinction from a standard leverage covenant that's always live.

## Why the stress test matters more than the base case

`output/stress_test.png` shows Excess Availability shrinking as accounts receivable and
inventory contract under increasingly severe working capital stress scenarios — exactly what
would happen in a real downturn (fewer sales, slower collections, inventory write-downs). The
**covenant only trips under the "Severe Stress" scenario (-35% AR, -25% Inventory)**, where
Excess Availability falls to just $1.52mm, below the $7.5mm threshold — meaning this facility
has a real, but not unlimited, cushion against a genuine business downturn. This is exactly the
analysis both the lender (assessing facility risk) and the borrower (assessing liquidity risk
under stress) would run before finalizing or renewing an ABL facility.
