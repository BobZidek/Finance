# Potential Enhancements

- **Cross-check against the full model**: run the same target's assumptions through
  `PE/full-lbo-model-business-services`'s detailed engine and quantify how far the quick
  calculator's IRR/MOIC diverge from the fully-modeled version.
- **Margin expansion toggle**: add an EBITDA margin expansion assumption on top of pure
  revenue-driven EBITDA growth, since real deals often underwrite margin improvement
  alongside growth.
- **Multiple hold-period comparison**: run 3/5/7-year hold scenarios side by side to show
  how IRR (which annualizes MOIC) and MOIC (which doesn't) can favor different hold lengths.
- **Fees and minimum cash**: add transaction fees to Uses and a minimum operating cash balance
  the debt paydown assumption must respect.
- **Interactive slider tool**: rebuild as a small Streamlit app so entry/exit multiple,
  leverage, and growth can be adjusted live with the sensitivity heatmap updating in real time
  — matching how this kind of quick calculator is actually used in practice.
- **Downside case**: add a stress-test scenario (EBITDA decline, multiple compression) to show
  how quickly leverage's amplification effect works against the sponsor in a bad outcome.
