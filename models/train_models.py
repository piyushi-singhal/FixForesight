"""
Train Models Pipeline

Loads processed features, trains multiple models with randomized search,
handles imbalance with class weights or SMOTE (if available), evaluates,
saves best model and comparison CSV, and outputs plots.

Outputs:
- models/best_model.pkl
- models/model_comparison.csv
- reports/roc_curves.png
- reports/confusion_matrices.png
- reports/feature_importances.png

"""

from pathlib import Path
import logging
import warnings
from typing import Dict, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("train_models")
warnings.filterwarnings("ignore")


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Processed features not found at {path}")
    LOG.info(f"Loading processed features from {path}")
    return pd.read_csv(path)


def prepare_xy(df: pd.DataFrame, target_col: str = "Machine failure"):
    if target_col not in df.columns:
        alt = [c for c in df.columns if c.lower().replace(" ", "") == target_col.lower().replace(" ", "")]
        if alt:
            target_col = alt[0]
        else:
            raise KeyError(f"Target column '{target_col}' not found in dataframe")

    X = df.select_dtypes(include=[np.number]).copy()
    if target_col not in X.columns:
        # target may be non-numeric but we expect numeric
        X[target_col] = df[target_col]

    y = X.pop(target_col)
    
    # Sanitize feature names for XGBoost compatibility (remove brackets, angle brackets, etc.)
    X.columns = [col.replace('[', '_').replace(']', '_').replace('<', '_').replace('>', '_') for col in X.columns]
    
    return X, y


def stratified_split(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def get_models(random_state=42):
    models = {}
    models["logreg"] = LogisticRegression(solver="saga", max_iter=5000, random_state=random_state)
    models["rf"] = RandomForestClassifier(random_state=random_state, n_jobs=-1)
    models["gb"] = GradientBoostingClassifier(random_state=random_state)

    # xgboost and lightgbm may not be installed; import dynamically
    try:
        import xgboost as xgb

        models["xgb"] = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=random_state)
    except Exception:
        LOG.warning("xgboost not available; skipping XGBoost model")

    try:
        import lightgbm as lgb

        models["lgbm"] = lgb.LGBMClassifier(random_state=random_state)
    except Exception:
        LOG.warning("lightgbm not available; skipping LightGBM model")

    return models


def imbalance_strategy(X_train, y_train):
    # Prefer class_weight for tree-based and logistic; offer SMOTE if imblearn available
    try:
        from imblearn.over_sampling import SMOTE

        LOG.info("Using SMOTE for class balancing")
        sm = SMOTE(random_state=42)
        X_res, y_res = sm.fit_resample(X_train, y_train)
        return X_res, y_res
    except Exception:
        LOG.info("imblearn not available; using class weights during model training")
        return X_train, y_train


def param_distributions():
    return {
        "logreg": {"C": np.logspace(-4, 4, 20), "penalty": ["l2", "none"]},
        "rf": {"n_estimators": [100, 200, 400], "max_depth": [None, 5, 10, 20], "min_samples_split": [2, 5, 10]},
        "gb": {"n_estimators": [100, 200, 400], "learning_rate": [0.01, 0.05, 0.1], "max_depth": [3, 5, 8]},
        "xgb": {"n_estimators": [100, 200, 400], "learning_rate": [0.01, 0.05, 0.1], "max_depth": [3, 5, 8]},
        "lgbm": {"n_estimators": [100, 200, 400], "learning_rate": [0.01, 0.05, 0.1], "num_leaves": [31, 50, 100]},
    }


def randomized_search(model, params, X, y, n_iter=20, cv=3, scoring="roc_auc", random_state=42):
    rs = RandomizedSearchCV(model, params, n_iter=n_iter, cv=cv, scoring=scoring, random_state=random_state, n_jobs=-1)
    rs.fit(X, y)
    return rs


def evaluate_model(model, X_test, y_test) -> Dict[str, Any]:
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
    else:
        # fallback for models without predict_proba
        y_proba = model.decision_function(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else np.nan,
        "confusion_matrix": confusion_matrix(y_test, y_pred),
    }
    return metrics, y_proba


def plot_roc_curves(results: Dict[str, Dict], X_test, y_test, out_path: Path):
    plt.figure(figsize=(8, 6))
    for name, res in results.items():
        y_proba = res.get("y_proba")
        if y_proba is None:
            continue
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.plot(fpr, tpr, label=f"{name} (AUC={res['roc_auc']:.3f})")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path / "roc_curves.png")
    plt.close()


def plot_confusion_matrices(results: Dict[str, Dict], out_path: Path):
    n = len(results)
    cols = 2
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    axes = axes.flatten()
    for ax, (name, res) in zip(axes, results.items()):
        cm = res["confusion_matrix"]
        sns.heatmap(cm, annot=True, fmt="d", ax=ax, cmap="Blues")
        ax.set_title(name)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
    for ax in axes[len(results) :]:
        fig.delaxes(ax)
    plt.tight_layout()
    plt.savefig(out_path / "confusion_matrices.png")
    plt.close()


def plot_feature_importances(results: Dict[str, Dict], feature_names, out_path: Path):
    # Use the best model that has importances or coefficients
    best_name = None
    for name, res in results.items():
        if "feature_importance" in res:
            best_name = name
            break
    if best_name is None:
        LOG.info("No model with feature importances found")
        return
    fi = results[best_name]["feature_importance"]
    fi = pd.Series(fi, index=feature_names).sort_values(ascending=False)[:20]
    plt.figure(figsize=(8, max(4, len(fi) * 0.25)))
    fi.plot(kind="barh")
    plt.title(f"Feature importances ({best_name})")
    plt.tight_layout()
    plt.savefig(out_path / "feature_importances.png")
    plt.close()


def run_pipeline():
    base = Path(__file__).resolve().parents[1]
    processed_path = base / "data" / "processed_features.csv"
    out_models = base / "models"
    out_reports = base / "reports"
    out_models.mkdir(exist_ok=True)
    out_reports.mkdir(exist_ok=True)

    df = load_data(processed_path)
    X, y = prepare_xy(df, target_col="Machine failure")

    # Guard: ensure at least two classes present
    if y.nunique() < 2:
        LOG.error("Target variable has fewer than 2 classes; cannot train models.")
        out_models.mkdir(exist_ok=True)
        pd.DataFrame(columns=["model", "accuracy", "precision", "recall", "f1", "roc_auc"]).to_csv(out_models / "model_comparison.csv", index=False)
        return

    # Split
    X_train, X_test, y_train, y_test = stratified_split(X, y, test_size=0.2)

    # Handle imbalance
    X_train_bal, y_train_bal = imbalance_strategy(X_train, y_train)

    models = get_models()
    params = param_distributions()

    results = {}
    comparison_rows = []

    for name, model in models.items():
        LOG.info(f"Training {name}")
        model_params = params.get(name, {})

        # If class_weight supported, set to balanced
        if hasattr(model, "class_weight"):
            try:
                model.set_params(class_weight="balanced")
            except Exception:
                pass

        # Fit randomized search (use balanced training set)
        try:
            rs = randomized_search(model, model_params, X_train_bal, y_train_bal, n_iter=20)
            best = rs.best_estimator_
            LOG.info(f"Best params for {name}: {rs.best_params_}")
        except Exception as e:
            LOG.warning(f"RandomizedSearchCV failed for {name}: {e}; fitting default model")
            best = model.fit(X_train_bal, y_train_bal)

        metrics, y_proba = evaluate_model(best, X_test, y_test)
        # capture feature importances if available
        fi = None
        if hasattr(best, "feature_importances_"):
            fi = best.feature_importances_
        elif hasattr(best, "coef_"):
            fi = np.ravel(best.coef_)

        results[name] = {
            "model": best,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "roc_auc": metrics["roc_auc"],
            "confusion_matrix": metrics["confusion_matrix"],
            "y_proba": y_proba,
        }
        if fi is not None:
            results[name]["feature_importance"] = fi

        comparison_rows.append({
            "model": name,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "roc_auc": metrics["roc_auc"],
        })

    # Select best model by roc_auc then recall
    comp_df = pd.DataFrame(comparison_rows).set_index("model")
    comp_df.to_csv(out_models / "model_comparison.csv")

    # Determine best by roc_auc then recall
    comp_sorted = comp_df.sort_values(["roc_auc", "recall"], ascending=False)
    best_name = comp_sorted.index[0]
    best_model = results[best_name]["model"]

    # Save best model
    joblib.dump(best_model, out_models / "best_model.pkl")
    LOG.info(f"Saved best model ({best_name}) to {out_models / 'best_model.pkl'}")

    # Plots
    plot_roc_curves(results, X_test, y_test, out_reports)
    plot_confusion_matrices(results, out_reports)
    plot_feature_importances(results, X.columns.tolist(), out_reports)

    LOG.info("Training pipeline completed")
    print("Best model:", best_name)
    print(comp_df.sort_values(["roc_auc", "recall"], ascending=False).head())


if __name__ == "__main__":
    run_pipeline()
