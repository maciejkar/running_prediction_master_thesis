# Models Directory

This directory contains the trained machine learning models used for running performance prediction.

## Directory Structure

```
models/
├── best_pipeline/           # Best performing models for each algorithm
├── cv_results/             # Cross-validation results
└── grid_search/            # Grid search results
```

## Best Pipeline Models

The `best_pipeline/` directory contains the best performing models for each algorithm, trained on different datasets:

- `*_halfmarathon.joblib`: Models trained on half marathon data
- `*_marathon.joblib`: Models trained on marathon data
- `*_whole.joblib`: Models trained on combined dataset

Available model types:
- Linear Regression
- Ridge Regression
- Lasso Regression
- Elastic Net
- Support Vector Regression (SVR)
- Decision Tree
- Gradient Boosting
- Multi-layer Neural Network
- K-Nearest Neighbors

## Model Usage

To load and use a model:

```python
import joblib

# Load the model
model = joblib.load('models/best_pipeline/ModelName_dataset.joblib')

# Make predictions
predictions = model.predict(X_test)
```

Note: Some large model files (RandomForest models) are not included in the repository due to size limitations. These models can be retrained using the provided training scripts.