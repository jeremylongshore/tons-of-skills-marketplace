---
name: building-automl-pipelines
description: 'Build automated machine learning pipelines with feature engineering,
  model selection, and hyperparameter tuning.

  Use when automating ML workflows from data preparation through model deployment.

  Trigger with phrases like "build automl pipeline", "automate ml workflow", or "create
  automated training pipeline".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- ai
- deployment
- ml
compatibility: Designed for Claude Code
---
# Building Automl Pipelines

## Overview

Build an end-to-end AutoML pipeline: data checks, feature preprocessing, model search/tuning, evaluation, and exportable deployment artifacts. Use this when you want repeatable training runs with a clear budget (time/compute) and a structured output (configs, reports, and a runnable pipeline).

## Prerequisites

Before using this skill, ensure you have:

- Python environment with AutoML libraries (Auto-sklearn, TPOT, H2O AutoML, or PyCaret)
- Training dataset in accessible format (CSV, Parquet, or database)
- Understanding of problem type (classification, regression, time-series)
- Sufficient computational resources for automated search
- Knowledge of evaluation metrics appropriate for task
- Target variable and feature columns clearly defined

## Instructions

1. Identify problem type (binary/multi-class classification, regression, etc.)
2. Define evaluation metrics (accuracy, F1, RMSE, etc.)
3. Set time and resource budgets for AutoML search
4. Specify feature types and preprocessing needs
5. Determine model interpretability requirements
6. Load training data using Read tool
7. Perform initial data quality assessment
8. Configure train/validation/test split strategy
9. Define feature engineering transformations
10. Set up data validation checks
11. Initialize AutoML pipeline with configuration

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Complete Python implementation of AutoML pipeline
- Data loading and preprocessing functions
- Feature engineering transformations
- Model training and evaluation logic
- Hyperparameter search configuration
- Best model architecture and hyperparameters

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- **Auto-sklearn**: Automated scikit-learn pipeline construction with metalearning
- **TPOT**: Genetic programming for pipeline optimization
- **H2O AutoML**: Scalable AutoML with ensemble methods
- **PyCaret**: Low-code ML library with automated workflows
- Automated feature selection techniques
