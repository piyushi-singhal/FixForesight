from pathlib import Path
import pandas as pd

p = Path(__file__).resolve().parents[1] / "data" / "processed_features.csv"
print(f"Inspecting: {p}")

df = pd.read_csv(p)
print('Columns:', df.columns.tolist())
print('Shape:', df.shape)

# find target column robustly
target_col = None
for c in df.columns:
    if c.lower().replace(' ', '') == 'machinefailure':
        target_col = c
        break

if target_col is None:
    print('Target column not found')
else:
    print(f"Target column: {target_col}")
    print('\nValue counts:')
    print(df[target_col].value_counts(dropna=False).to_string())
    print('\nUnique values:', df[target_col].unique())
    ones = df[df[target_col]==1]
    zeros = df[df[target_col]==0]
    print(f"Count of 1s: {len(ones)}")
    if len(ones) > 0:
        print('\nFirst positive rows:')
        print(ones.head(10).to_string(index=False))

print('\nDtypes:')
print(df.dtypes.to_string())
