from pathlib import Path

import pandas as pd

# ---------------------------
# 1) Load the cleaned dataset
# ---------------------------
input_options = [
    Path("data/cleaned_ai4i.csv"),
    Path("data/FixForesight-cleaneddataset.csv"),
]

input_path = None
for path in input_options:
    if path.exists():
        input_path = path
        break

if input_path is None:
    raise FileNotFoundError(
        "No cleaned dataset found. Expected one of: "
        + ", ".join(str(p) for p in input_options)
    )

print(f"Loading dataset from: {input_path}")
df = pd.read_csv(input_path)

# ---------------------------
# 2) Create new engineered features
# ---------------------------
# Temperature difference between process and air temperature
df["temp_diff"] = df["Process temperature [K]"] - df["Air temperature [K]"]

# Power = rotational speed multiplied by torque
df["power"] = df["Rotational speed [rpm]"] * df["Torque [Nm]"]

# Wear rate = tool wear divided by rotational speed
df["wear_rate"] = df["Tool wear [min]"] / df["Rotational speed [rpm]"]

# ---------------------------
# 3) Show the first 5 rows
# ---------------------------
print("\nFirst 5 rows after feature engineering:")
print(df.head())

# ---------------------------
# 4) Show summary statistics for new features
# ---------------------------
new_feature_cols = ["temp_diff", "power", "wear_rate"]
print("\nSummary statistics for engineered features:")
print(df[new_feature_cols].describe())

# ---------------------------
# 5) Save the engineered dataset
# ---------------------------
output_path = Path("data/engineered_ai4i.csv")
df.to_csv(output_path, index=False)
print(f"\nSaved engineered dataset to: {output_path}")
