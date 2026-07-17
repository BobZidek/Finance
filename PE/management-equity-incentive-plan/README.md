# Management Equity Incentive Plan (MIP) with Ratchet Design — Bridgeway Logistics Partners

Models a tiered management "ratchet" incentive structure for a hypothetical PE-backed
logistics platform: management's share of total exit proceeds increases in steps as overall
deal performance improves, producing a dramatic MOIC acceleration for management relative to
the sponsor at strong exit outcomes.

For the theory behind ratchet design and why sponsors deliberately structure incentives this
way, see [`theory/mip_ratchet_theory.md`](theory/mip_ratchet_theory.md).

## What the code does

1. **Loads deal assumptions** ([`data/mip_assumptions.csv`](data/mip_assumptions.csv)) —
   sponsor and management initial investment amounts.
2. **Loads the ratchet tier schedule** ([`data/ratchet_tiers.csv`](data/ratchet_tiers.csv)) —
   4 tiers of management's % share of total exit proceeds, keyed to the total deal MOIC achieved.
3. **Computes the proceeds split** at 8 exit value scenarios ($300mm-$1,200mm): determines
   which tier applies based on total deal MOIC, splits exit proceeds accordingly, and computes
   both sponsor and management MOIC.
4. **Outputs**: a scenarios CSV, a summary text file, a stacked proceeds-split chart, and a
   dual-axis sponsor-vs-management MOIC comparison chart.

## Data note

The company and all deal terms are **fictional/illustrative** — a mechanics demonstration of
ratchet incentive design rather than an analysis of a real management incentive plan.

## How to run

```bash
cd code
pip install -r requirements.txt
python mip_model.py
```

Outputs are written to `output/`.

## Folder structure

```
management-equity-incentive-plan/
├── code/
│   ├── mip_model.py
│   └── requirements.txt
├── data/
│   ├── mip_assumptions.csv
│   └── ratchet_tiers.csv
├── theory/
│   └── mip_ratchet_theory.md
├── output/                  # generated scenarios, summary, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

| Exit Value | Management Share | Sponsor MOIC | Management MOIC |
|---|---|---|---|
| $300mm | 10.0% | 1.35x | 6.0x |
| $820mm | 25.0% | 3.08x | 41.0x |
| $1,200mm | 25.0% | 4.50x | **60.0x** |

- **Management's tiny initial check ($5mm vs. the sponsor's $200mm) combined with the ratchet
  produces a dramatic MOIC acceleration** — at the top exit scenario, management's 60.0x MOIC
  is more than 13x the sponsor's own 4.50x MOIC on the same deal outcome.
- **The ratchet only pays out meaningfully in scenarios where the sponsor is also doing
  exceptionally well** — management's top-tier 25% share only applies once the deal has
  already cleared 4.0x total MOIC, ensuring the incentive structure rewards genuinely
  outstanding outcomes for both parties simultaneously, not one at the other's expense.
