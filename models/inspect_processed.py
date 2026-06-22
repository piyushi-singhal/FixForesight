import pandas as pd
p='data/processed_features.csv'
print('PATH:',p)
try:
    df=pd.read_csv(p)
except Exception as e:
    print('ERROR reading file',e)
    raise
print('shape',df.shape)
print('\ncolumns:')
print(df.columns.tolist())
print('\ndtypes:')
print(df.dtypes)
if 'Machine failure' in df.columns:
    print('\nMachine failure value_counts:\n',df['Machine failure'].value_counts(dropna=False))
    print('\nunique values:', df['Machine failure'].unique())
    vc=df['Machine failure'].value_counts(normalize=True,dropna=False)*100
    print('\ndistribution (%)\n',vc)
else:
    print('\nTarget Missing')
