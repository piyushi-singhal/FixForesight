from pathlib import Path

import pandas as pd

# ---------------------------
# Step 1: Load the dataset
# ---------------------------
RAW_FILE = Path("data/ai4i2020.csv.xlsx")
OUTPUT_FILE = Path("data/ai4i2020_cleaned.csv")

print(f"Loading dataset from: {RAW_FILE}")
df = pd.read_excel(RAW_FILE)

# ---------------------------
# Step 2: Inspect the raw data
# ---------------------------
print("\n--- Raw dataset preview ---")
print(df.head())

print("\n--- Raw shape ---")
print(df.shape)

print("\n--- Raw columns ---")
print(df.columns.tolist())

print("\n--- Missing values before cleaning ---")
print(df.isna().sum())

print("\n--- Duplicate rows before cleaning ---")
print(df.duplicated().sum())

# ---------------------------
# Step 3: Clean column names
# ---------------------------
df.columns = df.columns.str.strip()

# ---------------------------
# Step 4: Clean text values
# ---------------------------
string_cols = df.select_dtypes(include=["object", "string"]).columns
for col in string_cols:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace({"nan": None, "None": None})

# ---------------------------
# Step 5: Convert numeric columns safely
# ---------------------------
for col in df.columns:
    if col not in string_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------
# Step 6: Remove duplicates
# ---------------------------
df = df.drop_duplicates().reset_index(drop=True)

# ---------------------------
# Step 7: Final validation
# ---------------------------
print("\n--- Missing values after cleaning ---")
print(df.isna().sum())

print("\n--- Duplicate rows after cleaning ---")
print(df.duplicated().sum())

print("\n--- Final cleaned shape ---")
print(df.shape)

print("\n--- Final cleaned data preview ---")
print(df.head())

# ---------------------------
# Step 8: Save cleaned dataset
# ---------------------------
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved cleaned dataset to: {OUTPUT_FILE}")

# Optional: print a quick summary for key numeric columns
print("\n--- Summary statistics ---")
print(df.describe(include="all").T)
