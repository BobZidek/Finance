# Potential Enhancements

- **Purchase price allocation (PPA)**: model the goodwill/intangible split explicitly and add
  incremental amortization of acquired intangibles (reduces pro forma NI further — currently
  simplified away).
- **Multi-year synergy ramp**: phase synergies in over 3 years (e.g. 33%/66%/100%) instead of
  assuming full run-rate synergies from year 1, and show year 1/2/3 accretion-dilution
  separately.
- **Balance sheet / leverage impact**: model pro forma debt/EBITDA or (for a bank specifically)
  pro forma tangible common equity ratio and CET1 impact — critical for bank M&A given
  regulatory capital requirements.
- **Excess cash financing option**: add a toggle for funding the cash portion from balance
  sheet cash (foregone interest income) instead of new debt, and compare.
- **Collar / exchange ratio mechanics**: for stock deals, model a fixed exchange ratio vs. a
  fixed-value collar and show how the effective premium moves with acquirer share price
  between signing and closing.
- **Tangible book value dilution / earnback**: the bank-specific standard M&A metric — how many
  years it takes pro forma tangible book value per share to recover to the pre-deal level.
- **Real deal data**: pull actual regional bank financials (from 10-Ks/10-Qs) for a real,
  named hypothetical pairing once live data access is available, rather than fictional names.
- **Interactive assumption sweep**: build a small Streamlit/dash app so cash%, premium, and
  synergies can be adjusted with sliders and the sensitivity heatmap updates live.
