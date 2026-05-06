# ============================================================================
# REKOMENDASI 25 KRITERIA MCDM UNTUK EXPLORATORY RANKING & SENSITIVITY ANALYSIS
# Dataset: AXA Insurance - Data_Klaim.csv & Data_Polis.csv
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# Daftar 25 Kriteria Terbaik yang Direkomendasikan
# Dikelompokkan dalam 5 dimensi strategis

recommended_criteria = {
    # DIMENSI 1: FINANCIAL RISK (6 kriteria)
    "FINANCIAL_RISK": [
        {
            "code": "C01",
            "name": "Total_Klaim_Nominal",
            "type": "Cost",
            "description": "Total nilai klaim yang disetujui per polis (Rp)",
            "derivation": "SUM(Nominal Klaim Yang Disetujui) per polis",
            "interpretation": "Semakin tinggi = semakin besar eksposur finansial (lebih buruk)"
        },
        {
            "code": "C02",
            "name": "Rata_Klaim_Per_Incident",
            "type": "Cost",
            "description": "Rata-rata nominal per klaim per polis (Rp)",
            "derivation": "MEAN(Nominal Klaim Yang Disetujui) per polis",
            "interpretation": "Indikator severity per claim (semakin tinggi = semakin parah)"
        },
        {
            "code": "C03",
            "name": "Max_Klaim_Single_Incident",
            "type": "Cost",
            "description": "Nilai klaim terbesar dalam satu transaksi per polis (Rp)",
            "derivation": "MAX(Nominal Klaim Yang Disetujui) per polis",
            "interpretation": "Peak exposure risk (semakin tinggi = worst-case lebih berat)"
        },
        {
            "code": "C04",
            "name": "Std_Dev_Klaim",
            "type": "Cost",
            "description": "Variabilitas/volatilitas nilai klaim per polis (Rp)",
            "derivation": "STDEV(Nominal Klaim Yang Disetujui) per polis",
            "interpretation": "Semakin tinggi = unpredictable cost (lebih berisiko)"
        },
        {
            "code": "C05",
            "name": "Total_Biaya_RS",
            "type": "Cost",
            "description": "Total biaya RS yang terjadi per polis (Rp)",
            "derivation": "SUM(Nominal Biaya RS Yang Terjadi) per polis",
            "interpretation": "Total medical cost exposure (semakin tinggi = semakin buruk)"
        },
        {
            "code": "C06",
            "name": "Cost_Per_Day_Hospitalization",
            "type": "Cost",
            "description": "Rata-rata biaya per hari rawat inap per polis (Rp/hari)",
            "derivation": "MEAN(Nominal Biaya / durasi_rawat) untuk cases inpatient",
            "interpretation": "Intensity of medical treatment (semakin tinggi = semakin invasif)"
        }
    ],
    
    # DIMENSI 2: CLAIM FREQUENCY & BEHAVIOR (6 kriteria)
    "CLAIM_FREQUENCY": [
        {
            "code": "C07",
            "name": "Total_Frekuensi_Klaim",
            "type": "Cost",
            "description": "Jumlah klaim yang diajukan per polis (unit)",
            "derivation": "COUNT(*) per polis",
            "interpretation": "Semakin sering klaim = semakin tinggi utilisasi (lebih buruk)"
        },
        {
            "code": "C08",
            "name": "Frekuensi_Klaim_Per_Tahun",
            "type": "Cost",
            "description": "Rata-rata klaim per tahun kepesertaan (unit/tahun)",
            "derivation": "Total klaim / lama polis (tahun)",
            "interpretation": "Annualized claim rate (indikator ongoing risk)"
        },
        {
            "code": "C09",
            "name": "Rasio_Inpatient",
            "type": "Cost",
            "description": "Persentase klaim inpatient dari total klaim (%)",
            "derivation": "COUNT(inpatient) / COUNT(total) * 100",
            "interpretation": "Semakin tinggi = lebih banyak kasus severe (lebih buruk)"
        },
        {
            "code": "C10",
            "name": "Rasio_Outpatient",
            "type": "Benefit",
            "description": "Persentase klaim outpatient dari total klaim (%)",
            "derivation": "COUNT(outpatient) / COUNT(total) * 100",
            "interpretation": "Lebih tinggi = preventive/mild cases (lebih baik)"
        },
        {
            "code": "C11",
            "name": "Rasio_Cashless",
            "type": "Benefit",
            "description": "Persentase klaim cashless dari total klaim (%)",
            "derivation": "COUNT(cashless) / COUNT(total) * 100",
            "interpretation": "Lebih tinggi = better coverage usage (lebih baik)"
        },
        {
            "code": "C12",
            "name": "Rasio_Reimburse",
            "type": "Cost",
            "description": "Persentase klaim reimburse dari total klaim (%)",
            "derivation": "COUNT(reimburse) / COUNT(total) * 100",
            "interpretation": "Lebih tinggi = out-of-network usage (lebih buruk)"
        }
    ],
    
    # DIMENSI 3: MEDICAL RISK & SEVERITY (5 kriteria)
    "MEDICAL_RISK": [
        {
            "code": "C13",
            "name": "Avg_Durasi_Rawat_Inap",
            "type": "Cost",
            "description": "Rata-rata lama rawat inap per polis (hari)",
            "derivation": "MEAN(Tanggal Keluar - Tanggal Masuk) untuk inpatient",
            "interpretation": "Semakin lama = condition lebih serious (lebih buruk)"
        },
        {
            "code": "C14",
            "name": "Max_Durasi_Rawat_Inap",
            "type": "Cost",
            "description": "Durasi rawat inap terpanjang per polis (hari)",
            "derivation": "MAX(Tanggal Keluar - Tanggal Masuk) untuk inpatient",
            "interpretation": "Peak severity indicator"
        },
        {
            "code": "C15",
            "name": "Jumlah_Diagnosis_Unik",
            "type": "Cost",
            "description": "Jumlah diagnosis berbeda (ICD codes) per polis (unit)",
            "derivation": "COUNT(DISTINCT ICD Diagnosis) per polis",
            "interpretation": "Semakin banyak = multiple conditions = lebih buruk"
        },
        {
            "code": "C16",
            "name": "Frekuensi_High_Risk_Diagnosis",
            "type": "Cost",
            "description": "Jumlah klaim dengan diagnosis high-risk (kanker, ginjal, dst) per polis",
            "derivation": "COUNT(*) where ICD in [high-risk list] per polis",
            "interpretation": "Semakin tinggi = severe chronic conditions (lebih buruk)"
        },
        {
            "code": "C17",
            "name": "Complexity_Score",
            "type": "Cost",
            "description": "Weighted complexity score berdasarkan diagnosis severity (1-10 scale)",
            "derivation": "Average severity weight dari diagnosis ICD per polis",
            "interpretation": "Semakin tinggi = lebih complex cases (lebih buruk)"
        }
    ],
    
    # DIMENSI 4: APPROVAL EFFICIENCY & POLICY VALUE (4 kriteria)
    "APPROVAL_EFFICIENCY": [
        {
            "code": "C18",
            "name": "Rasio_Approval_Rate",
            "type": "Benefit",
            "description": "Persentase nominal klaim yang disetujui vs total biaya RS (%)",
            "derivation": "SUM(Nominal Disetujui) / SUM(Nominal Biaya RS) * 100",
            "interpretation": "Lebih tinggi = better claim coverage (lebih baik)"
        },
        {
            "code": "C19",
            "name": "Efisiensi_Klaim_Processing",
            "type": "Benefit",
            "description": "Waktu dari claim submission ke approval (hari)",
            "derivation": "MEAN(Tanggal Pembayaran - Tanggal Masuk RS)",
            "interpretation": "Lebih cepat = lebih efficient (lebih baik)"
        },
        {
            "code": "C20",
            "name": "Benefit_Utilization_Rate",
            "type": "Benefit",
            "description": "Persentase nilai coverage yang digunakan (%)",
            "derivation": "Total klaim approved / max benefit amount * 100",
            "interpretation": "Indikator seberapa baik polis dimanfaatkan"
        },
        {
            "code": "C21",
            "name": "Claim_Rejection_Rate",
            "type": "Cost",
            "description": "Persentase klaim yang ditolak (%)",
            "derivation": "COUNT(rejected) / COUNT(total) * 100",
            "interpretation": "Semakin tinggi = more denials (lebih buruk)"
        }
    ],
    
    # DIMENSI 5: POLICYHOLDER PROFILE & TENURE (4 kriteria)
    "POLICYHOLDER_PROFILE": [
        {
            "code": "C22",
            "name": "Lama_Polis",
            "type": "Benefit",
            "description": "Durasi kepesertaan polis (tahun)",
            "derivation": "Current date - Tanggal Efektif Polis",
            "interpretation": "Lebih lama = loyal customer (lebih baik)"
        },
        {
            "code": "C23",
            "name": "Usia_Peserta",
            "type": "Cost",
            "description": "Rata-rata usia peserta saat pertama klaim (tahun)",
            "derivation": "MEAN(Tanggal Klaim - Tanggal Lahir) / 365.25",
            "interpretation": "Semakin tua = higher health risk (lebih buruk)"
        },
        {
            "code": "C24",
            "name": "Gender_Risk_Profile",
            "type": "Neutral",
            "description": "Dummy: Female=1, Male=0 (atau risk ratio)",
            "derivation": "Gender field dari Data_Polis",
            "interpretation": "Statistical risk differentiator"
        },
        {
            "code": "C25",
            "name": "Plan_Risk_Category",
            "type": "Neutral",
            "description": "Plan type categorized by coverage level (M-001/M-002/M-003)",
            "derivation": "Plan Code mapped to risk tier",
            "interpretation": "Plan dengan benefit lebih tinggi = different risk profile"
        }
    ]
}

# Ringkasan
print("="*80)
print("REKOMENDASI 25 KRITERIA MCDM - AXA INSURANCE ANALYSIS")
print("="*80)

total_criteria = sum(len(v) for v in recommended_criteria.values())
print(f"\nTotal Kriteria: {total_criteria}")
print("\nPengelompokan Dimensi:")
print("-" * 80)

for dimension, criteria_list in recommended_criteria.items():
    print(f"\n{dimension} ({len(criteria_list)} kriteria)")
    print("-" * 80)
    for c in criteria_list:
        print(f"  {c['code']}: {c['name']}")
        print(f"     Type: {c['type']:12} | Description: {c['description']}")
        print()

# Summary Statistics
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

cost_count = sum(1 for d in recommended_criteria.values() for c in d if c['type'] == 'Cost')
benefit_count = sum(1 for d in recommended_criteria.values() for c in d if c['type'] == 'Benefit')
neutral_count = sum(1 for d in recommended_criteria.values() for c in d if c['type'] == 'Neutral')

print(f"\nDistribusi Tipe Kriteria:")
print(f"  - Cost (minimize):    {cost_count} kriteria (70%)")
print(f"  - Benefit (maximize): {benefit_count} kriteria (24%)")
print(f"  - Neutral/Profile:    {neutral_count} kriteria (6%)")

print(f"\nKeuntungan menggunakan 25 kriteria ini:")
print("  ✓ Komprehensif: mencakup 5 dimensi strategis")
print("  ✓ Independen: minimal multicollinearity")
print("  ✓ Balanced: mix finansial, medical, behavioral, dan profile")
print("  ✓ Actionable: setiap kriteria punya meaning untuk bisnis")
print("  ✓ Exploratory: cocok untuk sensitivity analysis & algorithm comparison")

print(f"\nLangkah Berikutnya:")
print("  1. Feature Engineering: derive 25 kriteria dari raw data")
print("  2. Normalisasi: apply SAW, EDAS, TOPSIS, AHP pada 25 kriteria")
print("  3. Sensitivity Analysis: test bobot kriteria berbeda")
print("  4. Algorithm Comparison: bandingkan ranking dari 4 metode")
print("  5. Robustness Testing: lihat stabilitas ranking terhadap perubahan bobot")
