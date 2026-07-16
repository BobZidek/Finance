# Sum-of-the-Parts (SOTP) Valuation — Meridian Industrial Group

Values a hypothetical diversified industrial conglomerate by applying each of its three
business segments' own peer trading multiple, nets out capitalized corporate overhead and net
debt, and compares the result against the company's current single-multiple trading value to
quantify the implied conglomerate discount — the standard analytical basis for a spin-off or
break-up thesis.

For the theory behind SOTP methodology and why a single blended multiple misprices a
conglomerate, see [`theory/sotp_valuation.md`](theory/sotp_valuation.md).

## What the code does

1. **Loads segment financials** ([`data/segments.csv`](data/segments.csv)) — revenue, EBITDA,
   and each segment's own peer EV/EBITDA multiple for Aerospace & Defense, Building Products,
   and Specialty Chemicals.
2. **Loads corporate-level assumptions** ([`data/corporate_assumptions.csv`](data/corporate_assumptions.csv))
   — unallocated corporate overhead EBITDA and its capitalization multiple, net debt, shares
   outstanding, and the company's current blended trading multiple.
3. **Computes SOTP Enterprise Value**: sum of each segment's own-multiple valuation, less
   capitalized corporate overhead.
4. **Computes SOTP Equity Value and per-share value**, and compares against the **current**
   trading value (using the single blended multiple) to quantify the **conglomerate discount**
   and the per-share upside a break-up could unlock.
5. **Builds a sensitivity table** sweeping all three segment multiples together (±1.5x).
6. **Outputs**: segment valuation CSV, sensitivity CSV, a summary text file, a SOTP bridge
   waterfall chart, and a current-vs-SOTP value-per-share comparison chart.

## Data note

The company and all segment financials are **fictional/illustrative** — a mechanics
demonstration of SOTP methodology rather than an analysis of a real conglomerate.

## How to run

```bash
cd code
pip install -r requirements.txt
python sotp_model.py
```

Outputs are written to `output/`.

## Folder structure

```
sum-of-the-parts-conglomerate/
├── code/
│   ├── sotp_model.py
│   └── requirements.txt
├── data/
│   ├── segments.csv
│   └── corporate_assumptions.csv
├── theory/
│   └── sotp_valuation.md
├── output/                  # generated segment valuations, sensitivity, charts
├── README.md
└── ENHANCEMENTS.md
```

## Key results (from the included assumptions)

- **SOTP Enterprise Value: $4,370mm** — Aerospace & Defense ($2,530mm at 11.5x) + Building
  Products ($1,395mm at 9.0x) + Specialty Chemicals ($760mm at 8.0x), less **$315mm of
  capitalized corporate overhead**.
- **SOTP value per share: $29.33**, vs. **current trading value of $23.02/share** (at the
  company's blended 8.5x multiple) — a **27.4% upside**.
- **Implied conglomerate discount: 17.3%** — the specific, quantified value a break-up or
  spin-off could unlock, not just a qualitative "conglomerates trade cheap" observation.
- The sensitivity table confirms the SOTP upside conclusion holds directionally across a wide
  range of segment multiple assumptions (±1.5x), not just the base case.
