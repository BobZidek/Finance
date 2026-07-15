# Potential Enhancements

- **Cross-sectional pooling**: instead of predicting a single asset's own time series, pool
  many correlated (or independent) assets' features and returns into one training set —
  applying the diversification logic from [`quant/multi-factor-stock-ranking`](../multi-factor-stock-ranking)
  to a time-series ML context, which real quant research typically does for exactly this reason.
- **Magnitude-weighted position sizing**: instead of a simple sign-based (+1/-1) position, size
  positions proportional to predicted return magnitude (or model confidence), which can
  perform differently than a pure directional bet even with the same underlying predictions.
- **Longer-horizon targets**: predict weekly or monthly returns instead of next-day returns,
  since return predictability (where it exists) is generally believed to be stronger at longer
  horizons than at daily frequency.
- **Walk-forward (rolling) retraining**: instead of one static train/test split, retrain the
  model periodically on a rolling window and evaluate cumulative walk-forward performance,
  more representative of how a real strategy would actually be deployed.
- **Feature importance / SHAP analysis**: for the Random Forest, analyze which features
  actually drove predictions, to check whether the model is recovering the true injected
  signal or picking up on spurious patterns.
- **Hyperparameter tuning with proper time-series cross-validation**: use `TimeSeriesSplit`
  cross-validation (not standard k-fold, which would leak future data) to tune Ridge's alpha
  and the Random Forest's depth/leaf-size parameters.
- **Real market data**: once live data access is available, replace the synthetic dataset with
  real historical prices and see how these same models perform on genuine (much weaker and
  noisier) real-world predictability.
