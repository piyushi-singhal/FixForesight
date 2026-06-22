import pandas as pd

df = pd.read_csv('data/processed_features.csv')
print('=== Processed Features CSV Verification ===')
print(f'Shape: {df.shape}')
print(f'Columns: {df.columns.tolist()}')
print('\nMachine failure value_counts:')
print(df['Machine failure'].value_counts())
print(f'\nUnique classes: {df["Machine failure"].unique()}')
print(f'\nData is ready for training: {len(df["Machine failure"].unique()) > 1}')
