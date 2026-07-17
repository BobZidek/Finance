# Potential Enhancements

- **Multi-year ROE projection**: replace the single-year LTM ROE with a forward multi-year
  projection (loan growth, net interest margin trends, credit cost normalization), since bank
  valuations are typically built on forward, not trailing, ROE.
- **Dividend discount model cross-check**: build a full DDM (dividends + terminal value) as a
  cross-check against the P/TBV framework, since both are theoretically consistent approaches
  to bank valuation.
- **Peer bank comps**: add a peer group of comparable banks with their own P/TBV and ROE, and
  regress P/TBV against ROE across the peer set (reusing the regression methodology from
  [`IB/comps-dashboard-saas`](../comps-dashboard-saas)) to cross-check the formula-implied multiple.
- **Credit quality overlay**: incorporate non-performing asset ratios and loan loss reserve
  adequacy into the valuation, since two banks with identical ROE can carry very different risk
  if one's ROE is inflated by under-reserving for credit losses.
- **Excess capital deployment scenarios**: model alternative uses of the excess capital
  (special dividend, buyback, M&A) and how each affects per-share value and blended ROE
  going forward.
- **Interest rate sensitivity**: add net interest margin sensitivity to a rising/falling rate
  environment, a first-order driver of bank earnings that a static ROE snapshot doesn't capture.
- **Real bank data**: once live market/regulatory data access is available, apply this
  framework to a real regional bank's actual reported financials and regulatory capital ratios.
