#!/usr/bin/env bash
# Preset: Python Data Science / ML

preset_name="python-data-science"
preset_description="Python Data Science / ML: Jupyter, pandas, scikit-learn, PyTorch, experiment tracking"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="notebook-hygiene.md|Notebook cell ordering, reproducibility, commit hygiene, production scripts
data-pipeline.md|pandas patterns, data loading, cleaning, transformation, memory optimization
cross-service.md|Virtual env management, experiment tracking, data versioning, logging"

# Technology stack entries
TECH_STACK="| Language | Python 3.11+ |
| Notebooks | Jupyter Lab / Jupyter Notebook |
| Data | pandas 2+, NumPy, polars (optional) |
| ML | scikit-learn, PyTorch / TensorFlow |
| Visualization | matplotlib, seaborn, plotly |
| Experiment Tracking | MLflow / Weights & Biases |
| Data Versioning | DVC (optional) |
| Linting | ruff (check + format), nbstripout |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New notebook** | \`.claude/rules/notebook-hygiene.md\`, \`notebooks/\` |
| **Data pipeline changes** | \`.claude/rules/data-pipeline.md\`, \`src/data/\`, \`src/features/\` |
| **Model work** | \`.claude/rules/data-pipeline.md\` (Modeling section), \`src/models/\` |
| **Environment/config** | \`.claude/rules/cross-service.md\`, \`requirements.txt\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Experiment results** | \`experiments/\`, \`mlruns/\` |"

# Context groups
CONTEXT_GROUPS='### `notebooks`
Read: `.claude/rules/notebook-hygiene.md`, `notebooks/`

### `data`
Read: `.claude/rules/data-pipeline.md`, `src/data/`, `src/features/`

### `models`
Read: `src/models/`, `src/training/`, `experiments/`

### `config`
Read: `.claude/rules/cross-service.md`, `configs/`, `requirements.txt`, `.env.example`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt       # or: pip install -e ".[dev]"

# Launch Jupyter
jupyter lab --port 8888

# Run a pipeline script
python src/data/make_dataset.py
python src/features/build_features.py
python src/models/train.py

# Run tests
pytest tests/ -v

# Lint
ruff check --fix .
ruff format .

# Strip notebook outputs before commit
nbstripout notebooks/*.ipynb

# Experiment tracking (MLflow)
mlflow ui --port 5000

# DVC (if using)
dvc pull                              # fetch data from remote
dvc repro                             # reproduce pipeline
```

### Key URLs

- Jupyter Lab: `http://localhost:8888`
- MLflow UI: `http://localhost:5000`
- TensorBoard (if using): `http://localhost:6006`'

# Project overview
PROJECT_OVERVIEW="Data science / ML project. Notebooks are for exploration; production code lives in \`src/\`."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── notebook-hygiene.md
│   │   ├── data-pipeline.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── data-issues.md
│   │   ├── model-experiments.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── notebooks/
│   ├── 01-exploration.ipynb
│   ├── 02-feature-engineering.ipynb
│   └── 03-modeling.ipynb
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── make_dataset.py
│   │   └── loaders.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   ├── visualization/
│   │   └── plots.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logging.py
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
├── configs/
│   ├── train_config.yaml
│   └── data_config.yaml
├── data/
│   ├── raw/           # immutable original data (gitignored)
│   ├── interim/       # intermediate transforms (gitignored)
│   ├── processed/     # final datasets (gitignored)
│   └── external/      # third-party data (gitignored)
├── models/            # serialized models (gitignored)
├── experiments/       # experiment logs, metrics
├── scripts/
│   └── smoke-project.sh
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── .gitignore
├── .dvcignore
├── requirements.txt
└── pyproject.toml'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-project.sh|Project Health Checks|SMOKE_PROJECT_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_PROJECT_CHECKS='section "Python Environment"

if [[ -d ".venv" ]] || [[ -n "$VIRTUAL_ENV" ]]; then
  pass "Virtual environment exists"
else
  warn "No .venv directory found — run: python -m venv .venv"
fi

if python3 -c "import pandas" 2>/dev/null; then
  pass "pandas is installed"
else
  fail "pandas is not installed (pip install pandas)"
fi

if python3 -c "import numpy" 2>/dev/null; then
  pass "NumPy is installed"
else
  fail "NumPy is not installed (pip install numpy)"
fi

if python3 -c "import sklearn" 2>/dev/null; then
  pass "scikit-learn is installed"
else
  warn "scikit-learn is not installed (pip install scikit-learn)"
fi

section "Jupyter"

if command -v jupyter >/dev/null 2>&1; then
  pass "Jupyter is installed"
else
  warn "Jupyter not found — run: pip install jupyterlab"
fi

if command -v nbstripout >/dev/null 2>&1; then
  pass "nbstripout is installed (notebook output stripping)"
else
  warn "nbstripout not installed — run: pip install nbstripout && nbstripout --install"
fi

section "Notebook Hygiene"

NOTEBOOKS_WITH_OUTPUT=0
for nb in notebooks/*.ipynb; do
  if [[ -f "$nb" ]]; then
    if python3 -c "
import json, sys
with open(\"$nb\") as f:
    nb = json.load(f)
for cell in nb.get(\"cells\", []):
    if cell.get(\"outputs\"):
        sys.exit(1)
" 2>/dev/null; then
      : # clean
    else
      NOTEBOOKS_WITH_OUTPUT=$((NOTEBOOKS_WITH_OUTPUT + 1))
    fi
  fi
done

if [[ $NOTEBOOKS_WITH_OUTPUT -eq 0 ]]; then
  pass "All notebooks have cleared outputs"
else
  warn "$NOTEBOOKS_WITH_OUTPUT notebook(s) have committed outputs — run: nbstripout notebooks/*.ipynb"
fi

section "Data Directories"

if [[ -d "data/raw" ]]; then
  pass "data/raw/ directory exists"
else
  warn "data/raw/ not found — create data directory structure"
fi

section "Configuration"

if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
  pass "Dependency file exists"
else
  warn "No requirements.txt or pyproject.toml found"
fi

section "Linting"

if command -v ruff >/dev/null 2>&1; then
  if ruff check --quiet src/ 2>/dev/null; then
    pass "ruff check passes on src/"
  else
    warn "ruff check has findings in src/"
  fi
else
  warn "ruff not installed"
fi

section "Tests"

if command -v pytest >/dev/null 2>&1; then
  if pytest --co -q 2>/dev/null | grep -q "test"; then
    pass "Tests discovered by pytest"
  else
    warn "No tests found"
  fi
else
  warn "pytest not installed"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Jupyter / Notebook

### Symptom: `ModuleNotFoundError` inside notebook but package is installed

**Diagnosis:** The Jupyter kernel is not using the same Python environment as your
terminal. The notebook kernel points to a different Python interpreter.

**Fix:**
```bash
# Ensure the kernel uses your venv
source .venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=project-env --display-name "Project (.venv)"
# Then select "Project (.venv)" kernel in Jupyter
```

---

### Symptom: Notebook produces different results on re-run

**Diagnosis:** Cells were executed out of order, or a cell depends on state from a
deleted cell. Hidden state accumulates in the kernel between runs.

**Fix:** Always run "Kernel > Restart & Run All" before considering results final.
Structure notebooks so cells run top-to-bottom without skipping. Never reference
variables defined in later cells.

---

## 2. Data / pandas

### Symptom: `MemoryError` or system becomes unresponsive when loading CSV

**Diagnosis:** The dataset is too large for available RAM. pandas loads entire DataFrames
into memory by default.

**Fix:**
```python
# 1. Specify dtypes to reduce memory
dtypes = {"user_id": "int32", "category": "category", "amount": "float32"}
df = pd.read_csv("data.csv", dtype=dtypes)

# 2. Load in chunks
chunks = pd.read_csv("data.csv", chunksize=100_000)
result = pd.concat([process(chunk) for chunk in chunks])

# 3. Use pyarrow backend (pandas 2+)
df = pd.read_csv("data.csv", engine="pyarrow", dtype_backend="pyarrow")

# 4. Switch to polars for out-of-core processing
import polars as pl
df = pl.scan_csv("data.csv").filter(pl.col("amount") > 0).collect()
```

---

### Symptom: `SettingWithCopyWarning` or silent mutation failures

**Diagnosis:** A chained indexing operation like `df[df.x > 0]["y"] = 1` creates a
temporary copy. The assignment modifies the copy, not the original DataFrame.

**Fix:**
```python
# BAD — chained indexing
df[df.x > 0]["y"] = 1

# GOOD — use .loc for label-based assignment
df.loc[df.x > 0, "y"] = 1

# GOOD — explicit copy when you want one
subset = df[df.x > 0].copy()
subset["y"] = 1
```

---

## 3. Model Training

### Symptom: Training loss decreases but validation loss increases after a few epochs

**Diagnosis:** The model is overfitting — memorizing training data rather than learning
generalizable patterns.

**Fix:**
```python
# 1. Add regularization
from sklearn.linear_model import Ridge
model = Ridge(alpha=1.0)  # L2 regularization

# 2. PyTorch: add dropout + early stopping
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, 10)

# 3. Reduce model complexity, increase training data, use cross-validation
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.3f} +/- {scores.std():.3f}")
```

---

## 4. Reproducibility

### Symptom: Results differ between runs despite same data and code

**Diagnosis:** Random state is not fixed. Many operations (train/test split, model
initialization, dropout, data shuffling) use random numbers.

**Fix:**
```python
import random
import numpy as np
import torch

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

# For full determinism in PyTorch (may reduce performance):
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# scikit-learn: pass random_state to every estimator
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="data-issues.md|Data loading problems, cleaning edge cases, dtype quirks
model-experiments.md|Experiment results, hyperparameters tried, lessons learned
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_NOTEBOOK_HYGIENE='# Notebook Hygiene

> **When to use:** Creating or reviewing Jupyter notebooks.
>
> **Read first for:** Any notebook work — cell structure, reproducibility, commit practices.

## Cell Ordering Standard

Every notebook MUST follow this cell order:

```
1. Title & Description (Markdown)    — purpose, data sources, expected outcome
2. Imports                           — ALL imports in a single cell at the top
3. Configuration / Constants         — paths, seeds, hyperparameters
4. Data Loading                      — read from disk/database/API
5. Data Exploration / EDA            — shape, dtypes, distributions, missing values
6. Data Cleaning / Preprocessing     — transformations, feature engineering
7. Modeling / Analysis               — train, fit, predict
8. Evaluation / Results              — metrics, plots, comparison tables
9. Conclusion (Markdown)             — summary of findings, next steps
```

### Rules

- **One purpose per notebook.** Split multi-topic work into separate notebooks.
- **Number notebooks** in execution order: `01-exploration.ipynb`, `02-features.ipynb`
- **Never skip cells.** Every cell must be runnable from "Restart & Run All."
- **No hidden state.** Do not rely on variables from deleted cells or out-of-order execution.

## Import Cell

```python
# Cell 1 — ALL imports here, nowhere else
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Project imports
from src.data.loaders import load_dataset
from src.features.build_features import engineer_features

# Configuration
warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 50)
%matplotlib inline
```

## Configuration Cell

```python
# Cell 2 — Constants and configuration
SEED = 42
DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
MODELS_DIR = Path("models")

# Reproducibility
np.random.seed(SEED)

# Hyperparameters (for modeling notebooks)
PARAMS = {
    "test_size": 0.2,
    "n_estimators": 100,
    "max_depth": 10,
}
```

## Reproducible Random Seeds

Set seeds **once** in the configuration cell, not scattered throughout:

```python
import random
import numpy as np
import torch

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
```

Always pass `random_state=SEED` to scikit-learn functions:

```python
X_train, X_test = train_test_split(X, y, random_state=SEED)
model = RandomForestClassifier(n_estimators=100, random_state=SEED)
```

## Commit Hygiene

### Clear Outputs Before Commit

Notebook outputs (plots, DataFrames, print statements) create large, noisy diffs.

```bash
# Install nbstripout (one-time setup)
pip install nbstripout
nbstripout --install                    # auto-strip on git add

# Manual strip
nbstripout notebooks/*.ipynb

# Verify no outputs remain
nbstripout --is-stripped notebooks/*.ipynb
```

### .gitignore for Notebooks

```
# Jupyter checkpoints
.ipynb_checkpoints/

# Large outputs saved as HTML
notebooks/*.html
```

## No Side Effects Between Cells

```python
# BAD — cell modifies global state that later cells depend on silently
df.drop(columns=["temp"], inplace=True)

# GOOD — explicit reassignment, no inplace mutation
df = df.drop(columns=["temp"])
```

- Never use `inplace=True`. Always reassign.
- Never mutate a DataFrame in one cell and read the mutation in another without clear variable assignment.
- If a cell defines a function, do not also call it in the same cell (separation of definition and execution).

## Production Equivalents

Every notebook that produces a result needed in production MUST have a `.py` script equivalent:

| Notebook | Script |
|----------|--------|
| `notebooks/02-feature-engineering.ipynb` | `src/features/build_features.py` |
| `notebooks/03-modeling.ipynb` | `src/models/train.py` |

The script should:
1. Accept command-line arguments (paths, hyperparameters)
2. Use `logging` instead of `print`
3. Save artifacts to disk (models, metrics JSON)
4. Be importable (wrap logic in functions, use `if __name__ == "__main__"`)

```python
# src/models/train.py
import argparse
import logging
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from src.data.loaders import load_dataset
from src.features.build_features import engineer_features

logger = logging.getLogger(__name__)

def train(data_path: Path, output_path: Path, seed: int = 42) -> dict:
    """Train model and save to disk. Returns metrics dict."""
    df = load_dataset(data_path)
    X, y = engineer_features(df)
    model = RandomForestClassifier(n_estimators=100, random_state=seed)
    model.fit(X, y)
    joblib.dump(model, output_path / "model.joblib")
    logger.info("Model saved to %s", output_path / "model.joblib")
    return {"accuracy": model.score(X, y)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=Path("models"))
    args = parser.parse_args()
    metrics = train(args.data, args.output)
    print(metrics)
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATA_PIPELINE='# Data Pipeline Patterns

> **When to use:** Loading, cleaning, transforming data. Building feature pipelines.
>
> **Read first for:** pandas operations, data loading, ML pipeline construction.

## Data Loading

### CSV with Explicit Types

```python
import pandas as pd

# Always specify dtypes — prevents silent type inference issues and saves memory
dtypes = {
    "user_id": "int64",
    "category": "category",         # huge memory savings for low-cardinality strings
    "amount": "float32",
    "date": "str",                  # parse dates separately for control
}

df = pd.read_csv(
    "data/raw/transactions.csv",
    dtype=dtypes,
    parse_dates=["date"],
    na_values=["", "NA", "null", "None"],
)
```

### Parquet (Preferred for Large Data)

```python
# Parquet preserves types, is columnar, and compresses well
df = pd.read_parquet("data/processed/features.parquet")

# Write with compression
df.to_parquet("data/processed/features.parquet", compression="snappy", index=False)
```

## Method Chaining with .pipe()

```python
def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"category": "category"})

def clean(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .dropna(subset=["user_id", "amount"])
        .drop_duplicates(subset=["transaction_id"])
        .assign(
            amount=lambda d: d["amount"].clip(lower=0),
            date=lambda d: pd.to_datetime(d["date"]),
        )
    )

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .assign(
            day_of_week=lambda d: d["date"].dt.dayofweek,
            month=lambda d: d["date"].dt.month,
            is_weekend=lambda d: d["date"].dt.dayofweek.isin([5, 6]),
            log_amount=lambda d: np.log1p(d["amount"]),
        )
    )

def validate(df: pd.DataFrame) -> pd.DataFrame:
    assert df["amount"].ge(0).all(), "Negative amounts found after cleaning"
    assert df["user_id"].notna().all(), "Null user_ids found"
    return df

# Compose the full pipeline
df = (
    load_raw("data/raw/transactions.csv")
    .pipe(clean)
    .pipe(add_features)
    .pipe(validate)
)
```

## Handling Missing Data

```python
# Check missing values
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
print(missing[missing > 0].sort_values(ascending=False))

# Strategy by column type
df = df.assign(
    # Numeric: fill with median (robust to outliers)
    income=lambda d: d["income"].fillna(d["income"].median()),
    # Categorical: fill with mode or explicit "Unknown"
    category=lambda d: d["category"].fillna("Unknown"),
    # Boolean: fill with False
    is_premium=lambda d: d["is_premium"].fillna(False),
)

# Drop rows where target is missing
df = df.dropna(subset=["target"])
```

## Merge / Join Patterns

```python
# Always specify how and validate
merged = pd.merge(
    users,
    orders,
    on="user_id",
    how="left",
    validate="one_to_many",      # raises if merge assumption violated
    indicator=True,              # adds _merge column for debugging
)

# Check merge quality
print(merged["_merge"].value_counts())
merged = merged.drop(columns=["_merge"])
```

## Memory Optimization

```python
def optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric types and convert low-cardinality strings to category."""
    for col in df.select_dtypes(include=["int"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].nunique() / len(df) < 0.5:  # less than 50% unique
            df[col] = df[col].astype("category")
    return df

# Check memory usage
print(df.info(memory_usage="deep"))
```

## scikit-learn Pipelines

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

numeric_features = ["age", "income", "log_amount"]
categorical_features = ["category", "region"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric_features),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical_features),
    ]
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
    )),
])

# Fit and evaluate
from sklearn.model_selection import train_test_split, cross_val_score

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
pipeline.fit(X_train, y_train)
print(f"Test accuracy: {pipeline.score(X_test, y_test):.4f}")

# Cross-validation
scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")
```

## Model Serialization

```python
import joblib
from pathlib import Path

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# Save
joblib.dump(pipeline, MODELS_DIR / "classifier_v1.joblib")

# Load
loaded_pipeline = joblib.load(MODELS_DIR / "classifier_v1.joblib")
predictions = loaded_pipeline.predict(X_new)
```

## PyTorch Patterns

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class SimpleNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

# Training loop
model = SimpleNet(input_dim=20, hidden_dim=128, output_dim=2).to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
criterion = nn.CrossEntropyLoss()

for epoch in range(50):
    model.train()
    total_loss = 0
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
        optimizer.zero_grad()
        output = model(X_batch)
        loss = criterion(output, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # Validation
    model.eval()
    with torch.no_grad():
        val_preds = model(X_val.to(DEVICE))
        val_loss = criterion(val_preds, y_val.to(DEVICE)).item()

# Save model
torch.save(model.state_dict(), "models/simple_net_v1.pt")
```

## Evaluation Patterns

```python
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    mean_squared_error,
    r2_score,
)

# Classification
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"ROC AUC: {roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]):.4f}")

# Regression
y_pred = model.predict(X_test)
print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.4f}")
print(f"R2:   {r2_score(y_test, y_pred):.4f}")
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, environment management, experiment tracking.
>
> **Read first for:** Virtual env setup, dependency pinning, experiment logging, data versioning.

## Virtual Environment Management

```bash
# Create venv (always use venv, never install globally)
python -m venv .venv
source .venv/bin/activate

# Pin all dependencies with exact versions
pip freeze > requirements.txt

# Better: use a layered approach
# requirements.txt     — production deps
# requirements-dev.txt — includes requirements.txt + dev tools
```

### requirements.txt Pinning

```
# requirements.txt — pin EXACT versions for reproducibility
numpy==1.26.4
pandas==2.2.1
scikit-learn==1.4.1
torch==2.2.1
matplotlib==3.8.3
seaborn==0.13.2
jupyterlab==4.1.2
```

**Rules:**
- Pin exact versions (`==`) in `requirements.txt` — never use `>=` for ML projects
- Update deliberately: `pip install --upgrade <pkg>` then re-freeze
- Keep separate files: `requirements.txt` (runtime), `requirements-dev.txt` (adds pytest, ruff, nbstripout)

## Experiment Tracking (MLflow)

```python
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("mlruns")       # local directory
mlflow.set_experiment("classification-v1")

with mlflow.start_run(run_name="gradient_boosting"):
    # Log parameters
    mlflow.log_params({
        "n_estimators": 200,
        "max_depth": 5,
        "learning_rate": 0.1,
        "test_size": 0.2,
    })

    # Train
    pipeline.fit(X_train, y_train)

    # Log metrics
    mlflow.log_metrics({
        "accuracy": pipeline.score(X_test, y_test),
        "roc_auc": roc_auc_score(y_test, pipeline.predict_proba(X_test)[:, 1]),
    })

    # Log model artifact
    mlflow.sklearn.log_model(pipeline, "model")

    # Log custom artifacts (plots, data profiles)
    mlflow.log_artifact("reports/confusion_matrix.png")
```

### Weights & Biases (Alternative)

```python
import wandb

wandb.init(project="my-project", config={"lr": 0.001, "epochs": 50})

for epoch in range(50):
    train_loss = train_one_epoch()
    val_loss = validate()
    wandb.log({"train_loss": train_loss, "val_loss": val_loss, "epoch": epoch})

wandb.finish()
```

## Data Versioning (DVC)

```bash
# Initialize DVC
dvc init

# Track large data files
dvc add data/raw/dataset.csv
git add data/raw/dataset.csv.dvc data/raw/.gitignore

# Push data to remote storage
dvc remote add -d storage s3://my-bucket/dvc
dvc push

# Reproduce pipeline
dvc repro
```

## .gitignore for Data Science

```
# Virtual environment
.venv/

# Jupyter
.ipynb_checkpoints/

# Data (managed by DVC or too large for git)
data/raw/
data/interim/
data/processed/
data/external/

# Models (serialized, often large)
models/*.joblib
models/*.pt
models/*.pkl
models/*.h5

# Experiment tracking
mlruns/
wandb/

# OS / IDE
.DS_Store
.idea/
.vscode/

# Environment secrets
.env
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `DATA_DIR` | `.env` / Config | Root data directory path |
| `MLFLOW_TRACKING_URI` | `.env` | MLflow server URL or local path |
| `WANDB_API_KEY` | `.env` / Secret | Weights & Biases API key |
| `AWS_ACCESS_KEY_ID` | `.env` / Secret | For S3 data access (DVC remote) |
| `RANDOM_SEED` | Config | Global random seed for reproducibility |

**API keys and secrets are NEVER committed to git.** Use `.env` locally.

```python
# src/utils/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
SEED = int(os.getenv("RANDOM_SEED", "42"))
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")
```

## Logging (Not Print)

```python
# In scripts (src/), use logging — never print()
import logging

logger = logging.getLogger(__name__)

def process_data(path):
    logger.info("Loading data from %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %d rows, %d columns", len(df), len(df.columns))
    # ...
    logger.warning("Found %d null values in target column", null_count)
    return df
```

`print()` is acceptable in notebooks for EDA output. In `src/` scripts, always use `logging`.

## Testing Conventions

```python
# tests/test_data.py
import pytest
import pandas as pd
from src.data.loaders import load_dataset
from src.features.build_features import engineer_features

@pytest.fixture
def sample_df():
    """Small deterministic DataFrame for testing."""
    return pd.DataFrame({
        "user_id": [1, 2, 3],
        "amount": [10.0, 20.0, 30.0],
        "category": ["A", "B", "A"],
    })

def test_load_dataset_returns_dataframe(tmp_path):
    csv_path = tmp_path / "test.csv"
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_csv(csv_path, index=False)
    result = load_dataset(csv_path)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

def test_engineer_features_adds_columns(sample_df):
    result = engineer_features(sample_df)
    assert "log_amount" in result.columns

def test_no_null_targets_after_cleaning(sample_df):
    from src.data.make_dataset import clean
    result = clean(sample_df)
    assert result["amount"].notna().all()
```

## Date/Time Format

All timestamps use **ISO 8601 UTC**: `2026-01-01T12:00:00Z`

```python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```'

LINT_LANGUAGES="Python (ruff check + ruff format), YAML, JSON, Shell (shellcheck), Jupyter (nbstripout)"
