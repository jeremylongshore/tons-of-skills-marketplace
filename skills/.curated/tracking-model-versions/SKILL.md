---
name: tracking-model-versions
description: 'Build this skill enables AI assistant to track and manage ai/ml model
  versions using the model-versioning-tracker plugin. it should be used when the user
  asks to manage model versions, track model lineage, log model performance, or implement
  version control f... Use when appropriate context detected. Trigger with relevant
  phrases based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- ai
- performance
- tracking-model
compatibility: Designed for Claude Code
---
# Model Versioning Tracker

## Overview

Track and manage AI/ML model versions using MLflow, DVC, or Weights & Biases. Log model metadata (hyperparameters, training data hash, framework version), record evaluation metrics (accuracy, F1, latency), manage model registry transitions (Staging, Production, Archived), and generate model cards documenting lineage and performance.

## Prerequisites

- MLflow tracking server running locally or remotely (`mlflow server` or managed MLflow)
- Python 3.9+ with `mlflow`, `pandas`, and the relevant ML framework installed
- Model artifacts accessible on the local filesystem or cloud storage (S3, GCS)
- Write access to the MLflow tracking URI and artifact store

## Instructions

1. Connect to the MLflow tracking server by setting `MLFLOW_TRACKING_URI` and verify connectivity with `mlflow experiments list`.
2. Create or select an MLflow experiment for the model project using `mlflow experiments create --experiment-name <name>`.
3. Log a new model version: start an MLflow run, log parameters (learning rate, epochs, batch size), log metrics (accuracy, loss, F1 score), and log the model artifact with `mlflow.<flavor>.log_model()`.
4. Register the model in the MLflow Model Registry using `mlflow.register_model()` with the run URI and a descriptive model name.
5. Transition the model version through stages: `None` -> `Staging` -> `Production` using `client.transition_model_version_stage()`. Archive previous production versions.
6. Compare model versions by querying metrics across runs with `mlflow.search_runs()` and generating comparison tables showing metric improvements between versions.
7. Generate a model card from the registered model metadata, including training data description, evaluation metrics, intended use, limitations, and ethical considerations. See [`assets/model_card_template.md`](assets/model_card_template.md).
8. Set up automated alerts for model performance degradation by comparing production metrics against baseline thresholds stored in the model registry.

See [`assets/example_mlflow_workflow.yaml`](assets/example_mlflow_workflow.yaml) for a complete workflow configuration.

## Examples

**Tracking a new image classification model version**: Log a ResNet-50 fine-tuned on a custom dataset. Record hyperparameters (lr=0.001, epochs=50, optimizer=Adam), metrics (val_accuracy=0.94, val_loss=0.18, inference_latency_ms=12), and the serialized model artifact. Register as version 3 in the model registry and transition to Staging for validation.

**Comparing model versions before production promotion**: Query MLflow for all versions of the sentiment-analysis model. Generate a comparison table showing accuracy improved from 0.87 (v2) to 0.91 (v3) while inference latency increased from 8ms to 15ms. Recommend promoting v3 to Production only if latency is acceptable for the use case.

**Generating a model card for compliance review**: Extract metadata from MLflow model registry version 5: training dataset (100K customer reviews), evaluation results (F1=0.89 on held-out test set), known limitations (struggles with sarcasm and multilingual input), and intended use (customer feedback classification). Output a structured Markdown model card.

## Output

- MLflow run with logged parameters, metrics, and model artifact
- Model registry entry with version number and stage assignment
- Version comparison table with metric deltas across runs
- Model card in Markdown format documenting lineage, performance, and limitations

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| MLflow connection refused | Tracking server not running or wrong URI | Verify `MLFLOW_TRACKING_URI` is correct; start server with `mlflow server --host 0.0.0.0 --port 5000` |
| Artifact upload failed | Insufficient permissions on artifact store | Check S3/GCS bucket permissions; verify IAM role has write access to the artifact path |
| Model registration conflict | Model name already exists with incompatible schema | Use a versioned model name or delete the conflicting registry entry |
| Metrics not logged | MLflow run ended before logging completed | Ensure all `log_metric()` calls happen within the active run context (`with mlflow.start_run():`) |
| Stage transition denied | Model version already in target stage | Archive the existing version in that stage first, then retry the transition |

## Resources

- MLflow documentation: https://mlflow.org/docs/latest/index.html
- MLflow Model Registry: https://mlflow.org/docs/latest/model-registry.html
- DVC (Data Version Control): https://dvc.org/doc
- Weights & Biases Model Registry:
- ML Model Cards: https://modelcards.withgoogle.com/about
