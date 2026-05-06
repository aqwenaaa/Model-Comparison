import pandas as pd
import os

base = r'd:/SEMESTER 6/PBL/Model-Comparison/dataset'
df_k = pd.read_csv(os.path.join(base, 'Data_Klaim.csv'))
df_p = pd.read_csv(os.path.join(base, 'Data_Polis.csv'))

print('Data_Klaim nrows', df_k.shape[0])
print('Data_Polis nrows', df_p.shape[0])
print('\nCategorical uniques:')
for col in ['Reimburse/Cashless', 'Inpatient/Outpatient', 'Status Klaim', 'Lokasi RS', 'Plan Code', 'Gender', 'Domisili']:
    if col in df_k.columns:
        print(col, df_k[col].nunique(), df_k[col].dropna().unique()[:10])
    else:
        print(col, df_p[col].nunique(), df_p[col].dropna().unique()[:10])

print('\nSample diagnosis values:')
print(df_k['ICD Diagnosis'].value_counts().head(10))
print('\nPlan codes:')
print(df_p['Plan Code'].value_counts())
print('\nGender:')
print(df_p['Gender'].value_counts())
print('\nDomisili top:')
print(df_p['Domisili'].value_counts().head(10))
print('\nClaim status:')
print(df_k['Status Klaim'].value_counts())
