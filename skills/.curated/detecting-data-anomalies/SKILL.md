---
name: detecting-data-anomalies
description: 'Process identify anomalies and outliers in datasets using machine learning
  algorithms.

  Use when analyzing data for unusual patterns, outliers, or unexpected deviations
  from normal behavior.

  Trigger with phrases like "detect anomalies", "find outliers", or "identify unusual
  patterns".

  '
allowed-tools: Read, Bash(python:*), Grep, Glob
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- ai
- ml
- detecting-data
compatibility: Designed for Claude Code
---
# Detecting Data Anomalies

## Overview

Identify anomalies and outliers in datasets using statistical and machine learning algorithms including Isolation Forest, One-Class SVM, Local Outlier Factor, and autoencoders. This skill handles the full detection pipeline from data ingestion and feature scaling through algorithm selection, threshold tuning, and result interpretation with anomaly scoring.

## Prerequisites

- Python 3.9+ with scikit-learn >= 1.3 (`pip install scikit-learn`)
- pandas and NumPy for data manipulation (`pip install pandas numpy`)
- matplotlib or seaborn for anomaly visualizations (`pip install matplotlib seaborn`)
- Dataset in CSV, JSON, Parquet, or database-queryable format
- Minimum 500 data points for statistical significance (1000+ recommended)
- Optional: PyTorch or TensorFlow for autoencoder-based detection on complex patterns

## Instructions

1. Load the dataset using the Read tool and verify schema, column types, and row count
2. Profile feature distributions using descriptive statistics to understand baseline behavior
3. Handle missing values via imputation (median for numeric, mode for categorical) or row exclusion
4. Apply StandardScaler or MinMaxScaler to numeric features to normalize magnitude differences
5. Select the detection algorithm based on data characteristics:
   - **Isolation Forest**: high-dimensional data, no assumptions on distribution
   - **One-Class SVM**: well-defined normal class with clear decision boundary
   - **Local Outlier Factor**: density-varying data with local anomaly patterns
   - **Autoencoder**: complex temporal or image data with non-linear relationships
6. Set the contamination parameter to the expected anomaly proportion (start with 0.01-0.05)
7. Fit the model on the training partition and generate anomaly scores for each data point
8. Apply the decision threshold to classify points as normal (-1) or anomalous (1)
9. Analyze flagged anomalies for common characteristics, temporal clusters, or feature correlations
10. Generate a summary report with detection counts, score distributions, and visualization plots

See [`references/implementation.md`](references/implementation.md) for the detailed implementation guide.

## Output

- Anomaly detection summary: total points, anomaly count, contamination rate
- Per-record anomaly scores with classification labels
- Algorithm configuration: model type, contamination, distance metric, threshold
- Feature importance ranking showing which dimensions drive anomaly flags
- Visualization: scatter plot of anomaly scores, distribution histogram, t-SNE cluster plot
- CSV export of flagged records with anomaly scores and contributing features

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Insufficient data volume | Fewer than 100 data points for model fitting | Collect additional data or switch to simple statistical methods (z-score, IQR) |
| High false positive rate | Contamination parameter set too high or features not scaled | Lower contamination to 0.01; verify StandardScaler applied; refine feature selection |
| Algorithm OOM on large dataset | Isolation Forest or LOF exceeds available memory | Subsample data for training; use `max_samples` parameter; switch to streaming approach |
| Feature scaling mismatch | Mixed numeric and categorical features without proper encoding | One-hot encode categoricals separately; scale numeric features independently |
| No ground truth for validation | Unlabeled dataset prevents accuracy measurement | Use domain expert review on top-N anomalies; implement feedback loop to refine threshold |

See [`references/errors.md`](references/errors.md) for the full error reference.

## Examples

**Scenario 1: Network Intrusion Detection** -- Apply Isolation Forest to 50K network flow records with features: packet count, byte volume, duration, protocol type. Expected contamination: 2%. Target: flag port-scan and DDoS patterns with precision above 0.85.

**Scenario 2: Manufacturing Quality Control** -- Run LOF on sensor readings (temperature, vibration, pressure) from 10K production cycles. Detect equipment degradation anomalies. Visualize flagged cycles on a time-series plot with normal operating bands.

**Scenario 3: Financial Transaction Monitoring** -- Train an autoencoder on 100K legitimate transactions. Reconstruct test transactions and flag those with reconstruction error above the 99th percentile. Report flagged transactions with amount, merchant category, and time-of-day features.

## Resources

- [scikit-learn Anomaly Detection](https://scikit-learn.org/stable/modules/outlier_detection.html) -- Isolation Forest, LOF, One-Class SVM
- [PyOD Library](https://pyod.readthedocs.io/) -- 40+ outlier detection algorithms with unified API
- Autoencoder anomaly detection: Keras/PyTorch reconstruction-error approach
- Feature scaling: StandardScaler, RobustScaler, MinMaxScaler selection guide
- Evaluation without labels: silhouette analysis, domain expert review protocols
