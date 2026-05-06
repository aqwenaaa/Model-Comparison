# ============================================================================
# MAPPING 25 KRITERIA KE ALTERNATIVE SELECTION & FEATURE ENGINEERING
# ============================================================================
"""
Dokumen ini mendokumentasikan:
1. 25 kriteria yang dipilih
2. Cara menderivasinya dari raw data
3. Mapping ke alternatif (polis) untuk ranking
4. Rencana bobot untuk sensitivity analysis
"""

import pandas as pd
import numpy as np

# ====================
# DAFTAR RINGKAS 25 KRITERIA
# ====================

CRITERIA_MAPPING = {
    # FINANCIAL RISK (C01-C06): 6 kriteria
    'C01_Total_Klaim': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp', 'weight_base': 0.06},
    'C02_Mean_Klaim': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp', 'weight_base': 0.05},
    'C03_Max_Klaim': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp', 'weight_base': 0.04},
    'C04_Std_Klaim': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp', 'weight_base': 0.04},
    'C05_Total_Biaya_RS': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp', 'weight_base': 0.05},
    'C06_Cost_Per_Day_LOS': {'dim': 'Financial', 'type': 'Cost', 'unit': 'Rp/hari', 'weight_base': 0.03},
    
    # CLAIM FREQUENCY (C07-C12): 6 kriteria
    'C07_Total_Freq': {'dim': 'Frequency', 'type': 'Cost', 'unit': 'unit', 'weight_base': 0.06},
    'C08_Freq_Per_Year': {'dim': 'Frequency', 'type': 'Cost', 'unit': 'unit/yr', 'weight_base': 0.05},
    'C09_Pct_Inpatient': {'dim': 'Frequency', 'type': 'Cost', 'unit': '%', 'weight_base': 0.04},
    'C10_Pct_Outpatient': {'dim': 'Frequency', 'type': 'Benefit', 'unit': '%', 'weight_base': 0.04},
    'C11_Pct_Cashless': {'dim': 'Frequency', 'type': 'Benefit', 'unit': '%', 'weight_base': 0.03},
    'C12_Pct_Reimburse': {'dim': 'Frequency', 'type': 'Cost', 'unit': '%', 'weight_base': 0.02},
    
    # MEDICAL RISK (C13-C17): 5 kriteria
    'C13_Avg_LOS': {'dim': 'Medical', 'type': 'Cost', 'unit': 'hari', 'weight_base': 0.04},
    'C14_Max_LOS': {'dim': 'Medical', 'type': 'Cost', 'unit': 'hari', 'weight_base': 0.03},
    'C15_Unique_Diagnosis': {'dim': 'Medical', 'type': 'Cost', 'unit': 'unit', 'weight_base': 0.04},
    'C16_High_Risk_Freq': {'dim': 'Medical', 'type': 'Cost', 'unit': 'unit', 'weight_base': 0.05},
    'C17_Complexity_Score': {'dim': 'Medical', 'type': 'Cost', 'unit': 'score', 'weight_base': 0.04},
    
    # APPROVAL EFFICIENCY (C18-C21): 4 kriteria
    'C18_Approval_Rate': {'dim': 'Approval', 'type': 'Benefit', 'unit': '%', 'weight_base': 0.03},
    'C19_Processing_Days': {'dim': 'Approval', 'type': 'Benefit', 'unit': 'hari', 'weight_base': 0.02},
    'C20_Benefit_Util_Rate': {'dim': 'Approval', 'type': 'Benefit', 'unit': '%', 'weight_base': 0.02},
    'C21_Rejection_Rate': {'dim': 'Approval', 'type': 'Cost', 'unit': '%', 'weight_base': 0.02},
    
    # POLICYHOLDER PROFILE (C22-C25): 4 kriteria
    'C22_Tenure_Years': {'dim': 'Profile', 'type': 'Benefit', 'unit': 'tahun', 'weight_base': 0.03},
    'C23_Usia_Peserta': {'dim': 'Profile', 'type': 'Cost', 'unit': 'tahun', 'weight_base': 0.04},
    'C24_Gender': {'dim': 'Profile', 'type': 'Neutral', 'unit': 'kategori', 'weight_base': 0.01},
    'C25_Plan_Type': {'dim': 'Profile', 'type': 'Neutral', 'unit': 'kategori', 'weight_base': 0.01},
}

# Summary
print("="*80)
print("MAPPING 25 KRITERIA - FEATURE ENGINEERING CHECKLIST")
print("="*80)

# Group by dimension
by_dim = {}
for crit, meta in CRITERIA_MAPPING.items():
    dim = meta['dim']
    if dim not in by_dim:
        by_dim[dim] = []
    by_dim[dim].append(crit)

print(f"\nTotal Kriteria: {len(CRITERIA_MAPPING)}")
for dim, crits in sorted(by_dim.items()):
    print(f"  - {dim:15}: {len(crits):2} kriteria")

# Type distribution
cost = sum(1 for m in CRITERIA_MAPPING.values() if m['type'] == 'Cost')
benefit = sum(1 for m in CRITERIA_MAPPING.values() if m['type'] == 'Benefit')
neutral = sum(1 for m in CRITERIA_MAPPING.values() if m['type'] == 'Neutral')
print(f"\nTipe Kriteria:")
print(f"  - Cost (minimize):    {cost}")
print(f"  - Benefit (maximize): {benefit}")
print(f"  - Neutral (profile):  {neutral}")

# Base weight
total_weight = sum(m['weight_base'] for m in CRITERIA_MAPPING.values())
print(f"\nTotal Base Weight: {total_weight:.2f}")

print("\n" + "="*80)
print("FEATURE ENGINEERING PSEUDOCODE")
print("="*80)

pseudocode = """
For each POLIS (alternative):
  
  [FINANCIAL RISK - C01 to C06]
  C01_Total_Klaim = SUM(Nominal_Disetujui) 
  C02_Mean_Klaim = MEAN(Nominal_Disetujui)
  C03_Max_Klaim = MAX(Nominal_Disetujui)
  C04_Std_Klaim = STDEV(Nominal_Disetujui)
  C05_Total_Biaya_RS = SUM(Nominal_Biaya_RS)
  C06_Cost_Per_Day_LOS = MEAN(Nominal_Biaya_RS / durasi_rawat) for inpatient only
  
  [CLAIM FREQUENCY - C07 to C12]
  C07_Total_Freq = COUNT(*) dari claims
  C08_Freq_Per_Year = COUNT(*) / tenure_years
  C09_Pct_Inpatient = COUNT(inpatient) / COUNT(*) * 100
  C10_Pct_Outpatient = COUNT(outpatient) / COUNT(*) * 100
  C11_Pct_Cashless = COUNT(cashless) / COUNT(*) * 100
  C12_Pct_Reimburse = COUNT(reimburse) / COUNT(*) * 100
  
  [MEDICAL RISK - C13 to C17]
  C13_Avg_LOS = MEAN(keluar_date - masuk_date) for inpatient
  C14_Max_LOS = MAX(keluar_date - masuk_date) for inpatient
  C15_Unique_Diagnosis = COUNT(DISTINCT ICD_Diagnosis)
  C16_High_Risk_Freq = COUNT(*) where ICD in [high-risk list]
  C17_Complexity_Score = MEAN(severity_weight) dari ICD diagnosis
  
  [APPROVAL EFFICIENCY - C18 to C21]
  C18_Approval_Rate = SUM(disetujui) / SUM(biaya_rs) * 100
  C19_Processing_Days = MEAN(bayar_date - masuk_date)
  C20_Benefit_Util_Rate = SUM(disetujui) / max_benefit * 100 (if available)
  C21_Rejection_Rate = COUNT(rejected) / COUNT(*) * 100
  
  [POLICYHOLDER PROFILE - C22 to C25]
  C22_Tenure_Years = (current_date - efektif_date) / 365.25
  C23_Usia_Peserta = MEAN(masuk_date - lahir_date) / 365.25
  C24_Gender = 1 if Female, 0 if Male
  C25_Plan_Type = Encode(Plan_Code) -> M-001=1, M-002=2, M-003=3
"""

print(pseudocode)

print("\n" + "="*80)
print("SENSITIVITY ANALYSIS PLAN")
print("="*80)

sa_plan = """
Scenario Weighting untuk Exploratory Analysis:

1. BASE CASE: Equal weight (1/25 = 0.04 untuk setiap kriteria)

2. FINANCIAL RISK HEAVY: 
   - Financial (C01-C06) weight: 50% (highest priority)
   - Frequency (C07-C12) weight: 25%
   - Medical/Approval/Profile weight: 25%

3. FREQUENCY RISK HEAVY:
   - Frequency (C07-C12) weight: 50%
   - Financial weight: 25%
   - Medical/Approval/Profile weight: 25%

4. MEDICAL RISK HEAVY:
   - Medical (C13-C17) weight: 50%
   - Financial/Frequency weight: 35%
   - Approval/Profile weight: 15%

5. BALANCED (RECOMMENDED):
   - Financial: 30%
   - Frequency: 30%
   - Medical: 25%
   - Approval: 10%
   - Profile: 5%

Untuk setiap scenario, run:
  - SAW (Simple Additive Weighting)
  - EDAS (Evaluation based on Distance from Average)
  - TOPSIS (Technique for Order Preference)
  - AHP (Analytic Hierarchy Process)

Output: Compare ranking stability across 4 algorithms x 5 weighting scenarios
"""

print(sa_plan)

print("\n" + "="*80)
print("DATA QUALITY & MISSING VALUE HANDLING")
print("="*80)

dq_notes = """
Berdasarkan data inspection sebelumnya:

1. C19_Processing_Days:
   ISSUE: Tanggal Pembayaran mungkin ada sebelum Tanggal Masuk (logical error)
   FIX: Gunakan Tanggal Pembayaran - Tanggal Klaim (jika ada), atau Tanggal Pembayaran - Tanggal Masuk
        Jika negatif, set ke 0 atau interpolate

2. C20_Benefit_Util_Rate:
   ISSUE: Max benefit amount tidak ada di dataset
   FIX: Drop kriteria ini ATAU gunakan proxy: (Total_Disetujui / Total_Biaya_RS)

3. C06_Cost_Per_Day_LOS:
   ISSUE: Hanya berlaku untuk inpatient cases (outpatient LOS = 0)
   FIX: Filter inpatient only, atau gunakan average untuk polis (mean dari valid days)
        Jika semua outpatient, set ke mean dari polis lain atau 0

4. C17_Complexity_Score:
   ISSUE: Severity weighting dari ICD codes tidak ada
   FIX: Kategorisasi manual high-risk vs low-risk (bisa dari medical knowledge)
        atau drop dan ganti dengan C16_High_Risk_Freq saja

5. C24_Gender & C25_Plan_Type:
   ISSUE: Categorical, bukan numeric
   FIX: Encode sebagai numeric (0/1 untuk Gender, 1/2/3 untuk Plan)
        Atau treat sebagai stratification variable, bukan kriteria scoring
"""

print(dq_notes)
