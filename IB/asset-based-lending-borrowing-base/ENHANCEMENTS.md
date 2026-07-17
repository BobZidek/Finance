# Potential Enhancements

- **Weekly/monthly rolling borrowing base**: extend from a single snapshot to a rolling
  time series of borrowing base certificates, showing how availability evolves month to month
  as AR and inventory naturally fluctuate with the business cycle.
- **Seasonality modeling**: add a seasonal working capital build/unwind pattern (common for
  distributors), showing how availability tightens during inventory build periods ahead of a
  peak selling season.
- **Multiple collateral categories**: split inventory into raw materials, work-in-process, and
  finished goods with different advance rates for each, more granular than the single blended
  inventory pool used here.
- **Fixed Charge Coverage Ratio (FCCR) test**: model the actual springing covenant test itself
  (not just whether it springs), since availability falling below the threshold triggers a
  coverage ratio test that could itself be breached.
- **Field exam / appraisal update cycle**: model periodic re-appraisal of NOLV% and periodic
  field exams that can adjust ineligibles, both standard ABL monitoring mechanisms that can
  tighten (or loosen) availability independent of the borrower's own reported AR/inventory levels.
- **Multi-tranche ABL + term loan structure**: layer a term loan tranche (e.g. secured by
  fixed assets/real estate) on top of the revolving ABL facility, a common combined structure.
- **Real borrower data**: once live data access is available, apply this framework to a real
  company's actual AR/inventory aging and facility terms.
