# 25 KRITERIA MCDM UNTUK AXA INSURANCE - RINGKASAN EKSEKUTIF

## OVERVIEW
Rekomendasi 25 kriteria untuk exploratory ranking dengan sensitivity analysis terhadap 4 algoritma MCDM (SAW, EDAS, TOPSIS, AHP).

---

## DAFTAR 25 KRITERIA (Ringkas)

### DIMENSI 1: FINANCIAL RISK (C01-C06) - 6 kriteria
| # | Kriteria | Type | Deskripsi |
|---|----------|------|-----------|
| C01 | Total_Klaim | Cost | Total nominal klaim per polis (Rp) |
| C02 | Mean_Klaim_Per_Incident | Cost | Rata-rata nilai per klaim (Rp) |
| C03 | Max_Klaim_Single_Incident | Cost | Peak claim value (Rp) |
| C04 | Std_Dev_Klaim | Cost | Volatility/variabilitas klaim (Rp) |
| C05 | Total_Biaya_RS | Cost | Total medical cost dari RS (Rp) |
| C06 | Cost_Per_Day_LOS | Cost | Rata-rata cost per hari rawat (Rp/hari) |

### DIMENSI 2: CLAIM FREQUENCY (C07-C12) - 6 kriteria
| # | Kriteria | Type | Deskripsi |
|---|----------|------|-----------|
| C07 | Total_Frekuensi_Klaim | Cost | Jumlah klaim diajukan (unit) |
| C08 | Frekuensi_Klaim_Per_Tahun | Cost | Annualized claim rate (unit/tahun) |
| C09 | Pct_Inpatient | Cost | % klaim inpatient dari total |
| C10 | Pct_Outpatient | Benefit | % klaim outpatient dari total |
| C11 | Pct_Cashless | Benefit | % klaim cashless dari total |
| C12 | Pct_Reimburse | Cost | % klaim reimburse dari total |

### DIMENSI 3: MEDICAL RISK (C13-C17) - 5 kriteria
| # | Kriteria | Type | Deskripsi |
|---|----------|------|-----------|
| C13 | Avg_Durasi_Rawat_Inap | Cost | Average length of stay (hari) |
| C14 | Max_Durasi_Rawat_Inap | Cost | Peak length of stay (hari) |
| C15 | Jumlah_Diagnosis_Unik | Cost | Jumlah diagnosis berbeda (unit) |
| C16 | Frekuensi_High_Risk_Diagnosis | Cost | Jumlah diagnosa risiko tinggi |
| C17 | Complexity_Score | Cost | Weighted severity score (1-10) |

### DIMENSI 4: APPROVAL EFFICIENCY (C18-C21) - 4 kriteria
| # | Kriteria | Type | Deskripsi |
|---|----------|------|-----------|
| C18 | Rasio_Approval_Rate | Benefit | % nominal approved / total biaya RS |
| C19 | Efisiensi_Klaim_Processing | Benefit | Hari dari klaim sampai bayar |
| C20 | Benefit_Utilization_Rate | Benefit | % benefit yang dipakai |
| C21 | Claim_Rejection_Rate | Cost | % klaim yang ditolak |

### DIMENSI 5: POLICYHOLDER PROFILE (C22-C25) - 4 kriteria
| # | Kriteria | Type | Deskripsi |
|---|----------|------|-----------|
| C22 | Lama_Polis | Benefit | Tenure kepesertaan (tahun) |
| C23 | Usia_Peserta | Cost | Average age saat klaim (tahun) |
| C24 | Gender_Risk_Profile | Neutral | Female=1, Male=0 |
| C25 | Plan_Risk_Category | Neutral | M-001, M-002, M-003 encoded |

---

## WEIGHTED DISTRIBUTION (Rekomendasi BALANCED)

```
Financial Risk  : 30% (C01-C06)    -> bobot = 0.05 per kriteria
Frequency Risk  : 30% (C07-C12)    -> bobot = 0.05 per kriteria
Medical Risk    : 25% (C13-C17)    -> bobot = 0.05 per kriteria
Approval Eff.   : 10% (C18-C21)    -> bobot = 0.025 per kriteria
Profile         :  5% (C22-C25)    -> bobot = 0.0125 per kriteria
                ------
TOTAL           : 100%
```

---

## SENSITIVITY ANALYSIS PLAN (5 Skenario)

### Scenario 1: EQUAL WEIGHT
- Semua 25 kriteria bobot = 1/25 = 0.04
- Baseline untuk comparison

### Scenario 2: FINANCIAL RISK HEAVY
- Financial (C01-C06): 50%
- Frequency (C07-C12): 25%
- Medical/Approval/Profile: 25%

### Scenario 3: FREQUENCY RISK HEAVY
- Frequency (C07-C12): 50%
- Financial (C01-C06): 25%
- Medical/Approval/Profile: 25%

### Scenario 4: MEDICAL RISK HEAVY
- Medical (C13-C17): 50%
- Financial/Frequency: 35%
- Approval/Profile: 15%

### Scenario 5: BALANCED (RECOMMENDED)
- Sesuai tabel distribusi di atas

---

## EXECUTION MATRIX

Untuk setiap skenario weighting, jalankan 4 algoritma:

```
          | Scenario1 | Scenario2 | Scenario3 | Scenario4 | Scenario5
          | (Equal)   | (Fin)     | (Freq)    | (Med)     | (Balanced)
----------|-----------|-----------|-----------|-----------|----------
SAW       | Rank A    | Rank A    | Rank A    | Rank A    | Rank A
EDAS      | Rank A    | Rank A    | Rank A    | Rank A    | Rank A
TOPSIS    | Rank A    | Rank A    | Rank A    | Rank A    | Rank A
AHP       | Rank A    | Rank A    | Rank A    | Rank A    | Rank A

Total: 4 algoritma x 5 skenario = 20 ranking outputs
```

**Output Analysis:**
1. Konsistensi ranking antar skenario untuk setiap algoritma
2. Sensitivitas algoritma terhadap perubahan bobot
3. Stabilitas top-K rankings
4. Korelasi Spearman antar algoritma per skenario

---

## DATA PREPARATION CHECKLIST

- [ ] Merge Data_Klaim.csv + Data_Polis.csv pada Nomor_Polis
- [ ] Handle missing values (tanggal negatif, LOS=0, dst)
- [ ] Derive 25 features per polis (aggregation)
- [ ] Normalisasi criteria (0-1 scale)
- [ ] Encode categorical (Gender, Plan_Type)
- [ ] Remove outliers jika diperlukan
- [ ] Sampling polis untuk analysis (50-100 alternatives)

---

## ALTERNATIF SELECTION

**Rekomendasi:** 80-100 polis sebagai alternatif
- Stratified sampling berdasarkan tenure, plan type, frequency
- Distribusi: new member (0-1yr), active (1-5yr), loyal (5+yr)

---

## EXPECTED OUTPUTS

1. **Ranking Tables** (5 skenario x 4 algoritma)
   - Top 10 best polis per metode & skenario

2. **Consistency Matrix**
   - Korelasi Spearman antar ranking

3. **Sensitivity Charts**
   - Perubahan ranking vs perubahan bobot
   - Stability scores

4. **Algorithm Comparison**
   - Which algorithm is most robust?
   - Which weighting scenario is most discriminative?

5. **Business Insights**
   - Polis dengan konsisten high ranking
   - Polis dengan inconsistent ranking
   - Feature importance ranking

---

## NOTES

- **C20_Benefit_Utilization_Rate**: Gunakan proxy jika max benefit tidak tersedia
- **C06 & C13-C14**: Filter inpatient only, handle outpatient dengan default/mean
- **C17_Complexity_Score**: Bisa drop jika ICD severity weights tidak ada
- **C24, C25**: Bisa treat sebagai stratification var, bukan scoring criteria

---

Prepared: May 5, 2026
Status: Ready for Implementation
