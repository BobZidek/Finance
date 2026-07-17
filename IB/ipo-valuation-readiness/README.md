# IPO Valuation & Readiness Model — Nimbus Cloud Systems

Builds a comps-based intrinsic valuation range for a hypothetical enterprise SaaS company
preparing for IPO, sets an offer price at a standard underwriting discount, and models the
full IPO mechanics: primary/secondary shares, the greenshoe over-allotment option, net
proceeds, post-IPO dilution and public float, and the quantified "money left on the table"
from deliberate IPO underpricing.

For the theory behind IPO underpricing and primary/secondary share mechanics, see
[`theory/ipo_valuation_theory.md`](theory/ipo_valuation_theory.md).

## What the code does

1. **Loads IPO assumptions** ([`data/ipo_assumptions.csv`](data/ipo_assumptions.csv)) —
   LTM revenue, comps multiple range, pre-IPO net cash and shares outstanding, offer price,
   primary/secondary share counts, greenshoe %, underwriting discount %.
2. **Computes a comps-based intrinsic valuation range** (EV/Revenue low-high) and per-share value.
3. **Computes full IPO mechanics**: gross/net primary proceeds, greenshoe shares, post-IPO
   share count and market cap, existing-holder dilution, public float %, and money left on the
   table relative to the intrinsic midpoint.
4. **Builds an offer-price sensitivity table** ($16-$22) showing how market cap, proceeds,
   dilution, and money-left-on-the-table all move with the pricing decision.
5. **Outputs**: a summary text file, a price sensitivity CSV, a valuation-range chart, and a
   post-IPO ownership pie chart.

## Data note

The company and all IPO terms are **fictional/illustrative** — a mechanics demonstration of
IPO valuation and pricing rather than an analysis of a real offering.

## How to run

```bash
cd code
pip install -r requirements.txt
python ipo_model.py
```

Outputs are written to `output/`.

## Folder structure

```
ipo-valuation-readiness/
├── code/
│   ├── ipo_model.py
│   └── requirements.txt
├── data/
│   └── ipo_assumptions.csv
├── theory/
│   └── ipo_valuation_theory.md
├── output/                  # generated summary, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **Comps-implied intrinsic range: $16.08 - $23.92/share** (6.0x-9.0x LTM Revenue), midpoint $20.00.
- **IPO priced at $18.00 — a deliberate 10% discount** to the intrinsic midpoint, standard
  underwriting practice to support aftermarket demand.
- **Net primary proceeds to the company: $242.4mm** (after underwriting fees, including the
  greenshoe).
- **Existing holders diluted from 100% to 89.3%**; **public float of 13.0%**.
- **$34.5mm left on the table** — the quantified cost of the 10% underpricing, a real trade-off
  every IPO pricing decision has to weigh.
