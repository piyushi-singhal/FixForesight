"""
Feature Engineering Pipeline

Implements dataset loading, inspection, encoding, feature creation,
outlier handling, feature selection, scaling, splitting, and saving
artifacts and visualizations.

Outputs:
- data/processed_features.csv
- models/scaler.pkl
- models/selected_features.pkl
- reports/feature_importance.png
- reports/correlation_heatmap.png
- reports/target_distribution.png
- reports/boxplots_outliers.png

Dependencies: pandas, numpy, matplotlib, seaborn, scikit-learn, joblib
"""

from pathlib import Path
import json
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib


LOG = logging.getLogger("feature_engineering")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_dataset(paths):
    for p in paths:
        p = Path(p)
        if p.exists():
            LOG.info(f"Loading dataset from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(f"None of the dataset files found: {paths}")


def inspect_dataset(df):
    LOG.info("Dataset preview:")
    LOG.info(f"Shape: {df.shape}")
    LOG.info(f"Columns: {df.columns.tolist()}")
    LOG.info("Dtypes:\n" + df.dtypes.to_string())


def remove_identifiers(df, cols_to_remove):
    existing = [c for c in cols_to_remove if c in df.columns]
    if existing:
        LOG.info(f"Removing identifier columns: {existing}")
        return df.drop(columns=existing)
    return df


def one_hot_encode(df, categorical_cols):
    cats = [c for c in categorical_cols if c in df.columns]
    if not cats:
        return df
    LOG.info(f"One-hot encoding: {cats}")
    return pd.get_dummies(df, columns=cats, drop_first=True)


def create_engineered_features(df):
    # Standardize expected column names for clarity
    # Accept several possible column namings
    col_map = {
        "air_temp": ["Air temperature [K]", "air_temperature", "AirTemperature"],
        "proc_temp": ["Process temperature [K]", "process_temperature", "ProcessTemperature"],
        "rot_speed": ["Rotational speed [rpm]", "rotational_speed", "RotationalSpeed"],
        "torque": ["Torque [Nm]", "torque", "TorqueNm"],
        "tool_wear": ["Tool wear [min]", "tool_wear", "ToolWear"],
    }

    def find_col(options):
        for o in options:
            if o in df.columns:
                return o
        return None

    air_col = find_col(col_map["air_temp"])
    proc_col = find_col(col_map["proc_temp"])
    speed_col = find_col(col_map["rot_speed"])
    torque_col = find_col(col_map["torque"])
    wear_col = find_col(col_map["tool_wear"])

    initial_feature_count = df.shape[1]

    # Temperature Difference = Air - Process
    if air_col and proc_col:
        df["temp_difference"] = df[air_col] - df[proc_col]

    # Power = Torque * Rotational Speed
    if torque_col and speed_col:
        df["power"] = df[torque_col] * df[speed_col]
        # Torque per RPM
        df["torque_per_rpm"] = df[torque_col] / (df[speed_col].replace(0, np.nan))

    # Temperature Efficiency Ratio = (Process - Air) / Air (relative rise)
    if air_col and proc_col:
        df["temp_efficiency_ratio"] = (df[proc_col] - df[air_col]) / (df[air_col].replace(0, np.nan))

    # Fill infinite/nan values from divisions
    df["torque_per_rpm"] = df["torque_per_rpm"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["temp_efficiency_ratio"] = df["temp_efficiency_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)

    final_feature_count = df.shape[1]
    LOG.info(f"Engineered features added: {final_feature_count - initial_feature_count}")
    return df, initial_feature_count, final_feature_count


def handle_outliers_iqr(df, numeric_cols):
    # Clip values to IQR fences
    LOG.info("Handling outliers using IQR clipping")
    for col in numeric_cols:
        if col not in df.columns:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        df[col] = df[col].clip(lower, upper)
    return df


def check_class_imbalance(df, target_col):
    if target_col not in df.columns:
        raise KeyError(f"Target column {target_col} not found in dataframe")
    counts = df[target_col].value_counts()
    ratio = (counts / counts.sum()).to_dict()
    LOG.info(f"Target distribution:\n{counts.to_string()}\nRatio: {ratio}")
    return counts


def correlation_analysis(df, target_col, corr_threshold=0.95):
    numeric = df.select_dtypes(include=[np.number])
    corr = numeric.corr()
    # Feature-target correlation
    if target_col in corr.columns:
        target_corr = corr[target_col].abs().sort_values(ascending=False)
    else:
        target_corr = None

    # Drop highly correlated features (upper triangle)
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column].abs() > corr_threshold)]
    LOG.info(f"Highly correlated features to consider dropping (>{corr_threshold}): {to_drop}")
    return corr, target_corr, to_drop


def feature_selection_random_forest(X, y, n_estimators=200, random_state=42):
    LOG.info("Running Random Forest for feature importance")
    rf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
    rf.fit(X, y)
    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    mean_imp = importances.mean()
    selected = importances[importances >= mean_imp].index.tolist()
    LOG.info(f"Selected {len(selected)} features (importance >= mean)")
    return importances, selected


def scale_and_split(df, feature_cols, target_col, test_size=0.15, val_size=0.15, random_state=42):
    X = df[feature_cols]
    y = df[target_col]

    # First split off test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    # Adjust validation split proportion relative to remaining
    val_relative = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative, stratify=y_train_val, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=feature_cols, index=X_train.index)
    X_val_scaled = pd.DataFrame(scaler.transform(X_val), columns=feature_cols, index=X_val.index)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=feature_cols, index=X_test.index)

    LOG.info(f"Shapes: train={X_train.shape}, val={X_val.shape}, test={X_test.shape}")
    return (X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, scaler)


def save_artifacts(df, feature_cols, scaler, selected_features, out_dir=Path(".")):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "data"
    models_path = out_dir / "models"
    reports_path = out_dir / "reports"
    data_path.mkdir(exist_ok=True)
    models_path.mkdir(exist_ok=True)
    reports_path.mkdir(exist_ok=True)

    processed_csv = data_path / "processed_features.csv"
    df.to_csv(processed_csv, index=False)
    joblib.dump(scaler, models_path / "scaler.pkl")
    joblib.dump(selected_features, models_path / "selected_features.pkl")
    LOG.info(f"Saved processed data to {processed_csv}")
    LOG.info(f"Saved scaler to {models_path / 'scaler.pkl'}")
    LOG.info(f"Saved selected features to {models_path / 'selected_features.pkl'}")
    return processed_csv, models_path, reports_path


def create_visualizations(importances, corr, df, target_col, reports_path: Path):
    sns.set(style="whitegrid")

    # Feature importance plot
    fig, ax = plt.subplots(figsize=(8, max(4, len(importances) * 0.2)))
    importances.sort_values().plot(kind="barh", ax=ax)
    ax.set_title("Feature Importances (Random Forest)")
    fig.tight_layout()
    fi_path = reports_path / "feature_importance.png"
    fig.savefig(fi_path)
    plt.close(fig)

    # Correlation heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    ch_path = reports_path / "correlation_heatmap.png"
    fig.tight_layout()
    fig.savefig(ch_path)
    plt.close(fig)

    # Target distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    df[target_col].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Target Class Distribution")
    td_path = reports_path / "target_distribution.png"
    fig.tight_layout()
    fig.savefig(td_path)
    plt.close(fig)

    # Boxplots for numeric columns (sampled if too many)
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    sample_cols = numeric if len(numeric) <= 10 else numeric[:10]
    fig, axes = plt.subplots(len(sample_cols), 1, figsize=(8, 4 * len(sample_cols)))
    if len(sample_cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, sample_cols):
        sns.boxplot(x=df[col], ax=ax)
        ax.set_title(f"Boxplot: {col}")
    bp_path = reports_path / "boxplots_outliers.png"
    fig.tight_layout()
    fig.savefig(bp_path)
    plt.close(fig)

    LOG.info(f"Saved visualizations to {reports_path}")


def main():
    base = Path(__file__).resolve().parents[1]
    data_paths = [base / "data" / "FixForesight-cleaneddataset.csv", base / "data" / "ai4i2020_cleaned.csv"]
    df = load_dataset(data_paths)

    inspect_dataset(df)

    # 3) Remove identifiers
    df = remove_identifiers(df, ["UDI", "Product ID"])  # case-sensitive as in file

    # 4) One-hot encode categorical variables
    df = one_hot_encode(df, ["Type"])

    # Track feature counts before engineering
    before_features = df.shape[1]

    # 5) Create engineered features
    df, feat_before, feat_after = create_engineered_features(df)

    # Numeric columns for outlier handling
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # 6) Handle outliers
    df = handle_outliers_iqr(df, numeric_cols)

    # 7) Check class imbalance for Machine failure
    target_col = "Machine failure"
    if target_col not in df.columns:
        # try alternative casing
        alt = [c for c in df.columns if c.lower().replace(" ", "") == "machinefailure"]
        if alt:
            target_col = alt[0]

    counts = check_class_imbalance(df, target_col)

    # 8) Correlation analysis
    corr, target_corr, to_drop = correlation_analysis(df, target_col)

    # Drop highly correlated features if any
    if to_drop:
        df = df.drop(columns=to_drop)

    # Prepare X and y
    feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns.tolist() if c != target_col]
    X = df[feature_cols].fillna(0)
    y = df[target_col]

    # Random Forest feature importance and selection
    importances, selected = feature_selection_random_forest(X, y)

    # Final feature list
    final_features = selected

    # Scaling and splitting
    X_train_s, X_val_s, X_test_s, y_train, y_val, y_test, scaler = scale_and_split(
        df, final_features, target_col
    )

    # Save artifacts
    processed_csv, models_path, reports_path = save_artifacts(df, final_features, scaler, final_features, base)

    # Visualizations
    create_visualizations(importances, corr, df, target_col, reports_path)

    # Display summaries
    print("\n=== Feature Engineering Summary ===")
    print(f"Final feature list ({len(final_features)}): {final_features}")
    print(f"Number of features before engineering: {before_features}")
    print(f"Number of features after engineering: {df.shape[1]}")
    print(f"Train shape: {X_train_s.shape}, Val shape: {X_val_s.shape}, Test shape: {X_test_s.shape}")


if __name__ == "__main__":
    main()
