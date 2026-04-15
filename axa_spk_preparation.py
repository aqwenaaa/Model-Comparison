"""
================================================================================
SISTEM PENDUKUNG KEPUTUSAN (SPK) - AXA INSURANCE
Framework : CRISP-DM
Tahap     : Data Understanding (Fase 1) + Data Preparation (Fase 2)
Tujuan    : Menghasilkan AXA_Prepared_Data.csv yang bersih dan feature-rich
Author    : Senior Data Scientist
================================================================================

CATATAN METODOLOGI:
Skrip ini dirancang secara modular mengikuti prinsip Single Responsibility
per fungsi. Setiap fungsi memiliki satu tugas spesifik agar mudah di-debug,
diuji secara terpisah, dan dimodifikasi tanpa menimbulkan efek samping.

Alur eksekusi:
  1. Audit kualitas data mentah (Data Understanding)
  2. Pembersihan dan perbaikan tipe data
  3. Penggabungan dua dataset
  4. Feature Engineering lanjutan
  5. Encoding dan Normalisasi
  6. Ekspor file master
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import warnings
import os

warnings.filterwarnings("ignore")


# ==============================================================================
# BAGIAN 1: KONSTANTA DAN KONFIGURASI
# ==============================================================================

# Path input data - sesuaikan jika diperlukan
PATH_POLIS  = "Data_Polis.csv"
PATH_KLAIM  = "Data_Klaim.csv"
PATH_OUTPUT = "AXA_Prepared_Data.csv"

# Kolom tanggal di masing-masing dataset
DATE_COLS_KLAIM = [
    "Tanggal Pembayaran Klaim",
    "Tanggal Pasien Masuk RS",
    "Tanggal Pasien Keluar RS",
]

# Kolom numerik yang akan dinormalisasi pada tahap akhir
NUMERIC_COLS_TO_SCALE = [
    "Nominal Klaim Yang Disetujui",
    "Nominal Biaya RS Yang Terjadi",
    "Cost_Gap",
    "Patient_Age",
    "Policy_Tenure_Days",
    "Treatment_Duration",
    "Claim_Frequency",
]

# Kategorisasi lokasi RS menjadi zona risiko biaya
LOKASI_RISK_MAP = {
    "Indonesia"  : 1,   # Biaya dasar, risiko paling rendah
    "Malaysia"   : 2,   # Biaya menengah
    "Others"     : 2,   # Disamakan dengan menengah
    "Overseas"   : 3,   # Biaya tinggi
    "Taiwan"     : 3,
    "Hong Kong"  : 3,
    "Tiongkok"   : 3,
    "Australia"  : 4,   # Biaya sangat tinggi
    "Singapore"  : 4,   # Biaya sangat tinggi
    "Japan"      : 4,
}


# ==============================================================================
# BAGIAN 2: DATA LOADING
# ==============================================================================

def load_raw_data(path_polis: str, path_klaim: str) -> tuple:
    """
    Memuat data mentah dari dua file CSV ke dalam DataFrame terpisah.

    Logika:
    Fungsi ini dirancang sebagai entry point tunggal untuk semua operasi baca
    data. Dengan memusatkan pembacaan di sini, kita memudahkan penggantian
    sumber data (misalnya dari database) tanpa mengubah kode di tahap hilir.

    Tanggal di Data_Polis disimpan sebagai integer format YYYYMMDD (bukan
    string), sehingga perlu diperlakukan berbeda dari kolom tanggal di
    Data_Klaim yang berformat string M/D/YYYY.

    Returns:
        Tuple (df_polis, df_klaim) berisi DataFrame masing-masing file.
    """
    print("[LOAD] Membaca Data_Polis.csv ...")
    df_polis = pd.read_csv(path_polis)

    print("[LOAD] Membaca Data_Klaim.csv ...")
    df_klaim = pd.read_csv(path_klaim)

    print(f"  -> Polis  : {df_polis.shape[0]:,} baris | {df_polis.shape[1]} kolom")
    print(f"  -> Klaim  : {df_klaim.shape[0]:,} baris | {df_klaim.shape[1]} kolom")

    return df_polis, df_klaim


# ==============================================================================
# BAGIAN 3: DATA UNDERSTANDING - AUDIT & PROFILING
# ==============================================================================

def audit_data_quality(df: pd.DataFrame, nama_dataset: str) -> pd.DataFrame:
    """
    Menghasilkan laporan kualitas data yang komprehensif untuk satu DataFrame.

    Logika:
    Audit dilakukan di tiga dimensi utama:
      (a) Kelengkapan   : jumlah dan persentase missing values per kolom
      (b) Keunikan      : deteksi duplikasi baris penuh
      (c) Tipe data     : apakah tipe sudah sesuai dengan konten kolom

    Laporan ini menjadi fondasi keputusan strategi penanganan data di
    tahap berikutnya. Jika missing values di bawah 5 persen, metode imputasi
    lebih disukai daripada penghapusan baris (untuk mempertahankan ukuran
    sampel yang memadai bagi pemodelan anomali).

    Returns:
        DataFrame berisi ringkasan kualitas per kolom.
    """
    print(f"\n{'='*60}")
    print(f" AUDIT KUALITAS DATA: {nama_dataset.upper()}")
    print(f"{'='*60}")
    print(f"  Dimensi  : {df.shape[0]:,} baris x {df.shape[1]} kolom")
    print(f"  Duplikat : {df.duplicated().sum()} baris")

    # Bangun tabel ringkasan kualitas
    summary = pd.DataFrame({
        "Tipe_Data"    : df.dtypes,
        "Jumlah_Non_Null": df.notnull().sum(),
        "Jumlah_Null"  : df.isnull().sum(),
        "Persen_Null"  : (df.isnull().sum() / len(df) * 100).round(2),
        "Unik_Value"   : df.nunique(),
    })

    print("\n  RINGKASAN KUALITAS PER KOLOM:")
    print(summary.to_string())

    # Analisis deskriptif khusus kolom numerik
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        print("\n  STATISTIK DESKRIPTIF KOLOM NUMERIK:")
        desc = df[numeric_cols].describe().T
        desc["CoV (%)"] = (desc["std"] / desc["mean"] * 100).round(1)
        print(desc.to_string())

    return summary


def audit_referential_integrity(df_polis: pd.DataFrame,
                                df_klaim: pd.DataFrame) -> dict:
    """
    Memeriksa integritas referensial antara Nomor Polis di kedua dataset.

    Logika:
    Integritas referensial berarti setiap Nomor Polis yang muncul di tabel
    Klaim WAJIB ada di tabel Polis (foreign key constraint). Jika ada klaim
    dengan Nomor Polis tidak dikenal, ini merupakan data anomali yang harus
    dikecualikan sebelum proses merge agar tidak menghasilkan baris NaN massal.

    Sebaliknya, nasabah di tabel Polis yang tidak memiliki klaim adalah data
    valid (nasabah aktif tanpa klaim). Ini adalah kondisi yang wajar dan
    memberikan informasi penting: nasabah dengan tenure panjang tanpa klaim
    dapat menjadi baseline profil risiko rendah.

    Returns:
        Dictionary berisi statistik integritas referensial.
    """
    print(f"\n{'='*60}")
    print(" AUDIT INTEGRITAS REFERENSIAL")
    print(f"{'='*60}")

    ids_polis = set(df_polis["Nomor Polis"])
    ids_klaim = set(df_klaim["Nomor Polis"])

    orphan_klaim = ids_klaim - ids_polis    # Klaim tanpa polis induk
    polis_no_claim = ids_polis - ids_klaim  # Polis tanpa riwayat klaim

    print(f"  Unique Polis  : {len(ids_polis):,}")
    print(f"  Unique Polis berklaim : {len(ids_klaim):,}")
    print(f"  Polis tanpa klaim     : {len(polis_no_claim):,} "
          f"({len(polis_no_claim)/len(ids_polis)*100:.1f}%)")
    print(f"  Orphan Klaim (klaim tanpa induk polis): {len(orphan_klaim)}")

    if len(orphan_klaim) > 0:
        print(f"  [PERINGATAN] Ditemukan {len(orphan_klaim)} klaim dengan "
              f"Nomor Polis tidak valid. Akan dieksklusikan saat merge.")
    else:
        print("  [OK] Semua Nomor Polis di Klaim valid.")

    return {
        "total_polis"       : len(ids_polis),
        "polis_berklaim"    : len(ids_klaim),
        "polis_no_claim"    : len(polis_no_claim),
        "orphan_klaim"      : len(orphan_klaim),
    }


# ==============================================================================
# BAGIAN 4: DATA CLEANING
# ==============================================================================

def parse_integer_date(series: pd.Series) -> pd.Series:
    """
    Mengkonversi kolom tanggal berformat integer YYYYMMDD menjadi datetime.

    Logika:
    Data_Polis menyimpan tanggal sebagai bilangan bulat (contoh: 19640811
    untuk 11 Agustus 1964). Ini adalah pola umum di sistem legacy asuransi.
    Fungsi ini mengkonversi ke string dulu agar dapat di-parse oleh
    pd.to_datetime dengan format yang eksplisit.

    Nilai yang tidak dapat di-parse akan menjadi NaT (Not a Time)
    sehingga dapat diidentifikasi dan ditangani tanpa crash.
    """
    return pd.to_datetime(series.astype(str), format="%Y%m%d", errors="coerce")


def parse_string_date(series: pd.Series) -> pd.Series:
    """
    Mengkonversi kolom tanggal berformat string M/D/YYYY menjadi datetime.

    Logika:
    Data_Klaim menggunakan format tanggal M/D/YYYY (tanpa padding nol,
    seperti '5/27/2024'). Parameter dayfirst=False memastikan pandas
    memprioritaskan urutan bulan-hari yang benar sesuai format Amerika.
    Penggunaan errors='coerce' mengkonversi nilai tidak valid menjadi NaT
    daripada menghentikan eksekusi dengan exception.
    """
    return pd.to_datetime(series, dayfirst=False, errors="coerce")


def clean_polis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan dan memperbaiki tipe data pada DataFrame Polis.

    Logika:
    Dua kolom tanggal (Tanggal Lahir dan Tanggal Efektif Polis) disimpan
    sebagai integer dan perlu dikonversi ke datetime. Pembersihan ini bersifat
    non-destruktif: tidak ada baris yang dihapus karena Data_Polis tidak
    memiliki missing values (berdasarkan hasil audit).
    """
    print("\n[CLEAN] Membersihkan Data_Polis ...")
    df = df.copy()

    df["Tanggal Lahir"]          = parse_integer_date(df["Tanggal Lahir"])
    df["Tanggal Efektif Polis"]  = parse_integer_date(df["Tanggal Efektif Polis"])

    invalid_dob = df["Tanggal Lahir"].isnull().sum()
    invalid_eff = df["Tanggal Efektif Polis"].isnull().sum()
    print(f"  Tanggal Lahir invalid (NaT)         : {invalid_dob}")
    print(f"  Tanggal Efektif Polis invalid (NaT) : {invalid_eff}")
    print(f"  [OK] Polis bersih: {len(df):,} baris")

    return df


def clean_klaim(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan Data_Klaim dengan penanganan missing values yang cerdas.

    Logika penanganan missing values (per kolom):

    1. Inpatient/Outpatient (37 missing):
       Diisi dengan 'UNKNOWN' karena tidak ada informasi kontekstual yang
       cukup untuk melakukan imputasi berbasis distribusi. Membiarkan string
       'UNKNOWN' lebih jujur daripada mengisi modus karena dapat bias.

    2. Tanggal Pembayaran Klaim (37 missing):
       Kondisi ini terjadi pada klaim yang belum selesai diproses. Nilai NaT
       dibiarkan apa adanya karena secara bisnis memang tidak ada tanggal bayar.
       Fitur turunan dari kolom ini akan menggunakan nilai 0 atau flag khusus.

    3. Lokasi RS (7 missing):
       Diisi dengan 'Indonesia' (modus). Secara logika bisnis, jika lokasi
       tidak tercatat, kemungkinan besar ini adalah RS domestik yang sistemnya
       belum terintegrasi penuh dengan sistem pencatatan klaim.

    4. ICD Diagnosis + ICD Description (6 missing bersamaan):
       Diisi dengan 'Z99.9' (Unspecified) sesuai standar ICD-10 WHO untuk
       diagnosis yang tidak dapat dikategorikan. Ini lebih baik daripada
       menggunakan modus yang dapat salah merepresentasikan kondisi pasien.

    5. Nominal Klaim = 0 (13 baris):
       Baris dengan nilai klaim nol tetap dipertahankan. Klaim senilai nol
       dapat merepresentasikan klaim yang ditolak (tapi status-nya PAID di
       data ini), atau biaya di bawah deductible. Ini merupakan pola yang
       informatif untuk model anomali.
    """
    print("\n[CLEAN] Membersihkan Data_Klaim ...")
    df = df.copy()

    # Konversi kolom tanggal dari string ke datetime
    for col in DATE_COLS_KLAIM:
        df[col] = parse_string_date(df[col])

    # Imputasi missing values dengan justifikasi berbeda per kolom
    df["Inpatient/Outpatient"].fillna("UNKNOWN", inplace=True)
    df["Lokasi RS"].fillna("Indonesia", inplace=True)
    df["ICD Diagnosis"].fillna("Z99.9", inplace=True)
    df["ICD Description"].fillna("UNSPECIFIED DIAGNOSIS", inplace=True)
    # Tanggal Pembayaran Klaim yang NaT dibiarkan (alasan: klaim belum terbayar)

    print(f"  Inpatient/Outpatient null setelah imputasi: "
          f"{df['Inpatient/Outpatient'].isnull().sum()}")
    print(f"  Lokasi RS null setelah imputasi           : "
          f"{df['Lokasi RS'].isnull().sum()}")
    print(f"  ICD Diagnosis null setelah imputasi       : "
          f"{df['ICD Diagnosis'].isnull().sum()}")
    print(f"  [OK] Klaim bersih: {len(df):,} baris")

    return df


# ==============================================================================
# BAGIAN 5: MERGING
# ==============================================================================

def merge_datasets(df_polis: pd.DataFrame,
                   df_klaim: pd.DataFrame) -> pd.DataFrame:
    """
    Menggabungkan Data_Polis dan Data_Klaim menggunakan LEFT JOIN dari Klaim.

    Logika pemilihan jenis join:
    Kita menggunakan merge dengan how='inner' dari sisi Klaim terhadap Polis.
    Ini berarti: ambil semua baris Klaim yang memiliki pasangan valid di Polis,
    dan sertakan semua kolom dari Polis yang cocok.

    Alasan tidak menggunakan LEFT JOIN dari Polis:
    - Jika kita left join dari Polis, nasabah tanpa klaim akan menghasilkan
      ribuan baris dengan nilai NaN di semua kolom klaim.
    - Tujuan analisis ini adalah pemodelan perilaku klaim, bukan profil
      semua nasabah. Nasabah tanpa klaim diproses terpisah.

    Alasan tidak menggunakan OUTER JOIN:
    - Audit integritas menunjukkan tidak ada orphan klaim, sehingga inner
      dan left-from-klaim akan menghasilkan hasil yang identik.

    Returns:
        DataFrame gabungan dengan semua fitur dari kedua sumber data.
    """
    print("\n[MERGE] Menggabungkan dataset ...")

    df_merged = pd.merge(
        left  = df_klaim,
        right = df_polis,
        on    = "Nomor Polis",
        how   = "inner",
        suffixes=("_klaim", "_polis")
    )

    print(f"  Baris setelah merge : {len(df_merged):,}")
    print(f"  Kolom setelah merge : {df_merged.shape[1]}")
    print(f"  [OK] Merge selesai tanpa kehilangan data klaim.")

    return df_merged


# ==============================================================================
# BAGIAN 6: FEATURE ENGINEERING
# ==============================================================================

def fe_patient_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR: Patient_Age - Usia Pasien Saat Masuk RS

    Logika:
    Usia dihitung sebagai selisih tahun antara Tanggal Pasien Masuk RS dan
    Tanggal Lahir. Ini bukan sekadar tahun ini dikurangi tahun lahir, melainkan
    memperhitungkan apakah ulang tahun pasien sudah terlewat atau belum di
    tahun klaim tersebut (dengan menggunakan selisih hari dibagi 365.25
    untuk mengakomodasi tahun kabisat).

    Relevansi untuk modeling:
    Usia adalah prediktor kuat biaya klaim (korelasi positif). Nasabah
    berusia di atas 55 tahun secara statistik menghasilkan klaim lebih tinggi
    terutama untuk penyakit degeneratif (kanker, ginjal, jantung) yang
    dominan di top-10 diagnosis data ini.
    """
    df["Patient_Age"] = (
        (df["Tanggal Pasien Masuk RS"] - df["Tanggal Lahir"]).dt.days / 365.25
    ).round(1)

    # Tangani nilai negatif atau tidak masuk akal (usia < 0 atau > 110)
    df["Patient_Age"] = df["Patient_Age"].clip(lower=0, upper=110)

    return df


def fe_policy_tenure(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR: Policy_Tenure_Days - Durasi Kepesertaan Saat Klaim

    Logika:
    Tenure dihitung sebagai selisih hari antara tanggal efektif polis (awal
    kepesertaan) dan tanggal pasien masuk RS. Nilai positif berarti polis
    sudah aktif sebelum klaim, nilai negatif (jika ada) menandakan anomali
    serius: klaim diajukan sebelum polis aktif, yang merupakan sinyal fraud.

    Relevansi untuk modeling:
    Pola "New Policy Claims" adalah salah satu indikator fraud terkuat dalam
    industri asuransi. Nasabah yang mengajukan klaim besar dalam 90 hari
    pertama kepesertaan memiliki profil risiko tinggi. Fitur ini akan menjadi
    variabel kunci di Isolation Forest dan Decision Engine.
    """
    df["Policy_Tenure_Days"] = (
        df["Tanggal Pasien Masuk RS"] - df["Tanggal Efektif Polis"]
    ).dt.days

    short_tenure = (df["Policy_Tenure_Days"] < 90).sum()
    negative_tenure = (df["Policy_Tenure_Days"] < 0).sum()
    print(f"  Policy_Tenure < 90 hari (risiko tinggi) : {short_tenure}")
    print(f"  Policy_Tenure negatif (potensi anomali)  : {negative_tenure}")

    return df


def fe_claim_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR: Claim_Frequency - Frekuensi Klaim Per Nasabah

    Logika:
    Frekuensi klaim dihitung dengan melakukan groupby pada Nomor Polis dan
    menghitung jumlah baris (klaim) yang dimiliki setiap nasabah, lalu
    nilai ini di-map kembali ke setiap baris klaim nasabah tersebut.

    Ini adalah contoh aggregate feature: nilai fitur bukan properti satu
    klaim, melainkan properti nasabah yang di-inject ke level klaim.

    Relevansi untuk modeling:
    Klaim yang sangat sering (lebih dari 10 kali per nasabah) dapat mengindikasikan:
    (a) Kondisi kronis yang memerlukan perhatian khusus (seperti cuci darah)
    (b) Potensi over-utilization yang perlu diinvestigasi
    (c) Profil nasabah berisiko tinggi untuk proyeksi biaya masa depan
    """
    freq_map = df.groupby("Nomor Polis")["Claim ID"].transform("count")
    df["Claim_Frequency"] = freq_map

    freq_dist = df["Claim_Frequency"].describe()
    print(f"  Claim_Frequency - max: {freq_dist['max']:.0f}, "
          f"mean: {freq_dist['mean']:.1f}, "
          f"median: {freq_dist['50%']:.0f}")

    return df


def fe_cost_gap(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR: Cost_Gap - Selisih Biaya RS dan Klaim yang Disetujui

    Logika:
    Cost_Gap = Nominal Biaya RS - Nominal Klaim yang Disetujui

    Nilai positif berarti ada bagian biaya yang ditanggung nasabah sendiri
    (di atas limit pertanggungan). Nilai negatif atau nol berarti klaim
    disetujui melebihi atau sama dengan biaya yang dilaporkan (bisa terjadi
    karena perbedaan kurs, biaya admin, atau kesalahan input).

    Derivasi tambahan Cost_Gap_Ratio:
    Rasio ini menormalisasi gap terhadap total biaya RS. Ini lebih informatif
    daripada nilai absolut karena biaya RS berbeda sangat jauh antara
    faskes domestik dan luar negeri. Sebuah gap Rp 10 juta di RS Indonesia
    memiliki makna berbeda dengan gap yang sama di Singapura.

    Relevansi untuk modeling:
    Cost_Gap_Ratio yang sangat rendah (mendekati 0) pada klaim dengan biaya
    sangat tinggi mengindikasikan full coverage, sementara rasio tinggi
    mengindikasikan klaim yang dikurangi secara signifikan (bisa karena
    pengurangan fraud atau exclusion clause).
    """
    df["Cost_Gap"] = (
        df["Nominal Biaya RS Yang Terjadi"] - df["Nominal Klaim Yang Disetujui"]
    )

    # Rasio gap: berapa persen dari biaya RS yang tidak diklaim/disetujui
    df["Cost_Gap_Ratio"] = np.where(
        df["Nominal Biaya RS Yang Terjadi"] > 0,
        df["Cost_Gap"] / df["Nominal Biaya RS Yang Terjadi"],
        0
    ).round(4)

    negative_gap = (df["Cost_Gap"] < 0).sum()
    print(f"  Cost_Gap negatif (klaim > biaya RS)     : {negative_gap}")

    return df


def fe_treatment_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR: Treatment_Duration - Lama Rawat Inap (dalam hari)

    Logika:
    Treatment_Duration = Tanggal Keluar RS - Tanggal Masuk RS (dalam hari)

    Nilai 0 adalah normal untuk klaim rawat jalan (OP) atau prosedur one-day
    care (ODC). Namun nilai 0 pada klaim rawat inap (IP) perlu ditandai
    sebagai potensi data inconsistency.

    Derivasi tambahan Claim_Type_Flag:
    Flag biner yang membedakan apakah klaim ini rawat inap (1) atau bukan (0).
    Rawat inap secara historis menghasilkan biaya rata-rata 5-10x lebih tinggi
    dari rawat jalan, sehingga memiliki pengaruh besar pada model regresi biaya.

    Relevansi untuk modeling:
    Duration yang sangat panjang (misal lebih dari 30 hari) berkorelasi kuat
    dengan penyakit kritis seperti kanker stadium lanjut atau gagal ginjal
    terminal, yang merupakan dua diagnosis teratas dalam dataset ini.
    """
    df["Treatment_Duration"] = (
        df["Tanggal Pasien Keluar RS"] - df["Tanggal Pasien Masuk RS"]
    ).dt.days

    # Rawat inap dengan durasi 0 adalah potensi inkonsistensi
    ip_zero_duration = (
        (df["Inpatient/Outpatient"] == "IP") & (df["Treatment_Duration"] == 0)
    ).sum()
    print(f"  IP dengan durasi 0 hari (inkonsistensi) : {ip_zero_duration}")

    # Flag biner: rawat inap atau tidak
    df["Is_Inpatient"] = (df["Inpatient/Outpatient"] == "IP").astype(int)

    return df


def fe_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR TEMPORAL: Ekstraksi fitur waktu dari tanggal klaim

    Logika:
    Analisis musiman sangat relevan untuk konteks kenaikan 25.5 persen YoY.
    Kita perlu memahami apakah lonjakan klaim terjadi merata sepanjang tahun
    atau terkonsentrasi pada bulan tertentu (pola musiman).

    Fitur yang diekstrak:
    1. Month_Claim    : Bulan klaim masuk RS (1-12), untuk analisis musiman
    2. Quarter_Claim  : Kuartal klaim (Q1-Q4), untuk analisis tren YoY
    3. Year_Claim     : Tahun klaim, untuk membandingkan volume antar tahun
    4. Days_To_Payment: Selisih hari antara masuk RS dan pembayaran klaim.
       Ini mengukur efisiensi proses klaim. Processing time yang sangat
       panjang bisa mengindikasikan klaim dengan dispute atau verifikasi
       fraud yang kompleks.

    Relevansi untuk modeling:
    Analisis korelasi antara Month_Claim dan Nominal Klaim akan mengungkap
    apakah ada peak season (misalnya akhir tahun) yang berkontribusi pada
    kenaikan YoY yang dilaporkan.
    """
    masuk_col = "Tanggal Pasien Masuk RS"
    bayar_col = "Tanggal Pembayaran Klaim"

    df["Month_Claim"]   = df[masuk_col].dt.month
    df["Quarter_Claim"] = df[masuk_col].dt.quarter
    df["Year_Claim"]    = df[masuk_col].dt.year

    # Days_To_Payment: NaT menghasilkan NaN, yang kita isi dengan -1 sebagai
    # sentinel value (artinya: belum dibayar / tidak diketahui)
    df["Days_To_Payment"] = (
        df[bayar_col] - df[masuk_col]
    ).dt.days.fillna(-1).astype(int)

    print(f"  Distribusi Year_Claim  : {df['Year_Claim'].value_counts().sort_index().to_dict()}")
    print(f"  Distribusi Month_Claim : modus = bulan {df['Month_Claim'].mode()[0]}")

    return df


def fe_risk_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    FITUR RISIKO KOMPOSIT: Indikator risiko berbasis logika bisnis asuransi

    Logika:
    Fitur-fitur ini merepresentasikan pengetahuan domain (domain knowledge)
    dari underwriting asuransi. Ini adalah fitur hasil rekayasa manual yang
    menangkap pola risiko yang mungkin tidak terdeteksi oleh model ML murni.

    1. Lokasi_RS_Risk_Score (1-4):
       Skor risiko finansial berdasarkan lokasi RS. RS luar negeri memiliki
       biaya jauh lebih tinggi dan potensi moral hazard lebih besar (nasabah
       bepergian ke luar negeri khusus untuk mendapat layanan mahal).

    2. High_Value_Claim_Flag:
       Flag biner: 1 jika nominal klaim di atas persentil ke-90 dari
       keseluruhan data. Ini adalah pendekatan Dynamic Percentile Ranking
       awal yang akan dikembangkan lebih lanjut di tahap Decision Engine.
       Penggunaan persentil (bukan threshold absolut) memastikan definisi
       "klaim besar" beradaptasi dengan distribusi data aktual.

    3. New_Policy_Claim_Flag:
       Flag biner: 1 jika klaim terjadi dalam 90 hari pertama kepesertaan.
       Ini adalah salah satu indikator fraud paling kuat di industri asuransi.

    4. Chronic_Disease_Flag:
       Flag berdasarkan ICD code yang mengindikasikan penyakit kronis
       (gagal ginjal, kanker, diabetes, hipertensi). Penyakit kronis
       menghasilkan pola klaim berulang yang prediktif.

    5. Overseas_Treatment_Flag:
       Flag biner untuk perawatan di luar Indonesia. Klaim overseas
       rata-rata 3-5x lebih mahal dari domestik dan memerlukan verifikasi
       lebih ketat.
    """
    # Skor risiko lokasi RS
    df["Lokasi_RS_Risk_Score"] = df["Lokasi RS"].map(LOKASI_RISK_MAP).fillna(2)

    # High value claim flag (Dynamic Percentile: P90)
    p90_klaim = df["Nominal Klaim Yang Disetujui"].quantile(0.90)
    df["High_Value_Claim_Flag"] = (
        df["Nominal Klaim Yang Disetujui"] >= p90_klaim
    ).astype(int)
    print(f"  Threshold P90 Nominal Klaim : Rp {p90_klaim:,.0f}")
    print(f"  High_Value_Claim_Flag = 1   : {df['High_Value_Claim_Flag'].sum()} baris")

    # New policy claim flag (tenure < 90 hari)
    df["New_Policy_Claim_Flag"] = (df["Policy_Tenure_Days"] < 90).astype(int)

    # Penyakit kronis berdasarkan ICD-10 prefix
    chronic_icd_prefix = ("N18", "N19", "C", "E11", "E14", "I10", "I11",
                          "I12", "I13", "I25", "J44", "Z99")
    df["Chronic_Disease_Flag"] = df["ICD Diagnosis"].str.startswith(
        chronic_icd_prefix
    ).astype(int)

    # Overseas treatment flag
    df["Overseas_Treatment_Flag"] = (
        df["Lokasi RS"] != "Indonesia"
    ).astype(int)

    return df


def run_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orkestrasi semua fungsi feature engineering secara berurutan.

    Logika:
    Fungsi ini bertindak sebagai pipeline controller. Urutan eksekusi penting
    karena beberapa fitur bergantung pada fitur yang dibuat sebelumnya
    (misalnya, fe_risk_indicators memerlukan Policy_Tenure_Days yang dibuat
    oleh fe_policy_tenure).
    """
    print("\n[FEATURE ENGINEERING] Membangun fitur-fitur baru ...")

    df = fe_patient_age(df)
    df = fe_policy_tenure(df)
    df = fe_claim_frequency(df)
    df = fe_cost_gap(df)
    df = fe_treatment_duration(df)
    df = fe_temporal_features(df)
    df = fe_risk_indicators(df)

    new_features = [
        "Patient_Age", "Policy_Tenure_Days", "Claim_Frequency",
        "Cost_Gap", "Cost_Gap_Ratio", "Treatment_Duration",
        "Is_Inpatient", "Month_Claim", "Quarter_Claim", "Year_Claim",
        "Days_To_Payment", "Lokasi_RS_Risk_Score", "High_Value_Claim_Flag",
        "New_Policy_Claim_Flag", "Chronic_Disease_Flag",
        "Overseas_Treatment_Flag"
    ]
    print(f"\n  [OK] {len(new_features)} fitur baru berhasil dibuat:")
    for f in new_features:
        print(f"       - {f}")

    return df


# ==============================================================================
# BAGIAN 7: ENCODING DAN NORMALISASI
# ==============================================================================

def encode_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan encoding pada fitur kategorikal untuk kesiapan modeling.

    Logika pemilihan metode encoding:

    1. Label Encoding (untuk fitur ordinal atau biner dengan kardinalitas rendah):
       - Gender (M/F): 2 kategori, tidak ada hierarki natural
       - Reimburse/Cashless (R/C): 2 kategori
       - Inpatient/Outpatient (IP/OP/ODC/ODS/UNKNOWN): 5 kategori, ordinal lemah

    2. Frequency Encoding (untuk Domisili dan Lokasi RS):
       Teknik ini menggantikan kategori dengan frekuensi kemunculannya.
       Ini lebih informatif dari label encoding untuk kolom dengan kardinalitas
       menengah (lebih dari 10 kategori) karena menangkap informasi "seberapa
       umum" kategori tersebut dalam dataset. Kota dengan frekuensi tinggi
       (Surabaya, Jakarta) mendapat nilai tinggi yang mencerminkan populasi
       nasabah yang lebih besar.

    3. Plan Code (M-001/M-002/M-003):
       Di-encode dengan Label Encoder karena mewakili tingkat plan yang
       dapat diasumsikan memiliki urutan (M-001 = dasar, M-003 = premium).
       Asumsi ini perlu divalidasi dengan tim bisnis untuk modeling aktual.

    Catatan: ICD Diagnosis memiliki ratusan kategori unik. Untuk tahap ini,
    kita membuat ICD_Category (2 karakter pertama) sebagai simplifikasi
    yang tetap informatif secara klinis, lalu di-label-encode.
    """
    print("\n[ENCODING] Melakukan encoding fitur kategorikal ...")
    df = df.copy()
    le = LabelEncoder()

    # Label Encoding: Gender
    df["Gender_Encoded"] = le.fit_transform(df["Gender"].fillna("Unknown"))
    print(f"  Gender mapping         : {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Label Encoding: Reimburse/Cashless
    df["Reimburse_Encoded"] = le.fit_transform(
        df["Reimburse/Cashless"].fillna("Unknown")
    )
    print(f"  Reimburse mapping      : {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Label Encoding: Inpatient/Outpatient
    df["Care_Type_Encoded"] = le.fit_transform(
        df["Inpatient/Outpatient"].fillna("UNKNOWN")
    )
    print(f"  CareType mapping       : {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Label Encoding: Plan Code
    df["Plan_Code_Encoded"] = le.fit_transform(df["Plan Code"].fillna("Unknown"))
    print(f"  Plan Code mapping      : {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Frequency Encoding: Domisili
    domisili_freq = df["Domisili"].value_counts(normalize=True)
    df["Domisili_Freq_Encoded"] = df["Domisili"].map(domisili_freq).round(4)

    # Frequency Encoding: Lokasi RS
    lokasi_freq = df["Lokasi RS"].value_counts(normalize=True)
    df["Lokasi_RS_Freq_Encoded"] = df["Lokasi RS"].map(lokasi_freq).round(4)

    # ICD Category: 2 karakter pertama ICD code sebagai kelompok diagnosis
    df["ICD_Category"] = df["ICD Diagnosis"].str[:3].str.strip()
    df["ICD_Category_Encoded"] = le.fit_transform(
        df["ICD_Category"].fillna("Z99")
    )

    print(f"  [OK] 7 fitur encoded berhasil dibuat.")
    return df


def normalize_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan normalisasi Min-Max pada fitur numerik kontinu.

    Logika:
    Min-Max Scaling mengubah nilai ke rentang [0, 1] dengan formula:
        X_scaled = (X - X_min) / (X_max - X_min)

    Kita menggunakan Min-Max daripada Standardization (Z-Score) karena:
    1. Isolation Forest dan K-Means sensitif terhadap skala dan bekerja
       lebih baik dengan data yang di-bounded [0, 1]
    2. Distribusi beberapa kolom (Nominal Klaim) sangat skewed, sehingga
       Z-Score akan menghasilkan nilai outlier yang sangat ekstrem

    Kolom yang dinormalisasi disimpan dengan suffix '_Scaled' untuk
    mempertahankan nilai aslinya agar dapat diinterpretasikan oleh tim bisnis.
    """
    print("\n[NORMALISASI] Melakukan Min-Max Scaling pada fitur numerik ...")
    df = df.copy()
    scaler = MinMaxScaler()

    # Hanya normalisasi kolom yang nilainya valid (tanpa terlalu banyak NaN)
    valid_cols = [c for c in NUMERIC_COLS_TO_SCALE if c in df.columns]
    scaled_cols = [f"{c}_Scaled" for c in valid_cols]

    df[scaled_cols] = scaler.fit_transform(
        df[valid_cols].fillna(df[valid_cols].median())
    )

    print(f"  [OK] {len(scaled_cols)} kolom berhasil di-scale:")
    for col in scaled_cols:
        print(f"       - {col}: [{df[col].min():.4f} - {df[col].max():.4f}]")

    return df


# ==============================================================================
# BAGIAN 8: VALIDASI AKHIR DAN EXPORT
# ==============================================================================

def final_validation(df: pd.DataFrame) -> None:
    """
    Melakukan validasi akhir pada DataFrame sebelum ekspor.

    Logika:
    Validasi ini memastikan bahwa data yang akan diekspor memenuhi
    kriteria minimal kesiapan untuk modeling:
    1. Tidak ada missing values pada fitur-fitur kunci yang akan digunakan
       sebagai input model
    2. Semua kolom numerik memiliki nilai yang masuk akal (tidak infinity)
    3. Jumlah baris sesuai ekspektasi (tidak ada kehilangan data yang tidak
       disengaja selama proses transformasi)
    """
    print(f"\n{'='*60}")
    print(" VALIDASI AKHIR SEBELUM EKSPOR")
    print(f"{'='*60}")
    print(f"  Total baris          : {len(df):,}")
    print(f"  Total kolom          : {df.shape[1]}")

    # Cek missing values pada kolom yang di-scaled
    scaled_cols = [c for c in df.columns if c.endswith("_Scaled")]
    null_in_scaled = df[scaled_cols].isnull().sum().sum()
    print(f"  Null di kolom Scaled : {null_in_scaled}")

    # Cek nilai infinity
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_count = np.isinf(df[numeric_cols]).sum().sum()
    print(f"  Nilai infinity       : {inf_count}")

    # Cek feature engineered columns
    engineered_cols = [
        "Patient_Age", "Policy_Tenure_Days", "Claim_Frequency",
        "Cost_Gap", "Treatment_Duration", "Month_Claim"
    ]
    for col in engineered_cols:
        null_cnt = df[col].isnull().sum()
        status = "[OK]" if null_cnt == 0 else "[PERINGATAN]"
        print(f"  {status} {col}: {null_cnt} null values")


def export_prepared_data(df: pd.DataFrame, path_output: str) -> pd.DataFrame:
    """
    Mengekspor DataFrame final ke CSV dan mencetak ringkasan kolom output.

    Logika:
    Sebelum ekspor, kita membuang kolom datetime mentah yang sudah tidak
    diperlukan untuk modeling (sudah diekstrak menjadi fitur numerik).
    Ini mengurangi ukuran file dan menghindari confusion bagi model yang
    tidak dapat memproses tipe datetime secara langsung.

    Kolom Nomor Polis dan Claim ID tetap dipertahankan sebagai identifier
    untuk keperluan audit trail dan explainability (menelusuri prediksi
    kembali ke nasabah individual).

    Returns:
        DataFrame final yang sama persis dengan yang diekspor.
    """
    print(f"\n[EXPORT] Mengekspor data ke '{path_output}' ...")

    # Kolom yang akan di-drop sebelum ekspor (sudah diekstrak ke fitur)
    cols_to_drop = [
        "Tanggal Lahir",
        "Tanggal Efektif Polis",
        "Tanggal Pasien Masuk RS",
        "Tanggal Pasien Keluar RS",
        "Tanggal Pembayaran Klaim",
    ]
    df_export = df.drop(columns=cols_to_drop, errors="ignore")

    df_export.to_csv(path_output, index=False)

    file_size_kb = os.path.getsize(path_output) / 1024
    print(f"  [OK] File berhasil disimpan.")
    print(f"  Ukuran file  : {file_size_kb:.1f} KB")
    print(f"  Total baris  : {len(df_export):,}")
    print(f"  Total kolom  : {df_export.shape[1]}")

    print("\n  DAFTAR KOLOM FINAL:")
    for i, col in enumerate(df_export.columns, 1):
        dtype_str = str(df_export[col].dtype)
        null_pct  = df_export[col].isnull().mean() * 100
        print(f"  {i:3d}. {col:<45} | {dtype_str:<10} | null: {null_pct:.1f}%")

    return df_export


# ==============================================================================
# BAGIAN 9: MAIN PIPELINE
# ==============================================================================

def run_pipeline() -> pd.DataFrame:
    """
    Pipeline utama CRISP-DM: Data Understanding hingga Data Preparation.

    Logika arsitektur pipeline:
    Setiap tahap mengambil output dari tahap sebelumnya dan menghasilkan
    output yang lebih bersih / lebih kaya. Desain ini disebut 'transformation
    pipeline' dan memastikan setiap langkah dapat:
    (a) Dijalankan secara independen untuk debugging
    (b) Diganti implementasinya tanpa mempengaruhi langkah lain
    (c) Di-log dengan jelas untuk keperluan audit

    Returns:
        DataFrame final yang telah diekspor ke AXA_Prepared_Data.csv
    """
    print("=" * 60)
    print(" SPK AXA INSURANCE - DATA PREPARATION PIPELINE")
    print(" Framework: CRISP-DM | Fase: Data Understanding + Preparation")
    print("=" * 60)

    # ---- FASE 1: DATA LOADING ----
    df_polis, df_klaim = load_raw_data(PATH_POLIS, PATH_KLAIM)

    # ---- FASE 2: DATA UNDERSTANDING (Audit) ----
    audit_data_quality(df_polis, "Data Polis")
    audit_data_quality(df_klaim, "Data Klaim")
    audit_referential_integrity(df_polis, df_klaim)

    # ---- FASE 3: DATA CLEANING ----
    df_polis_clean = clean_polis(df_polis)
    df_klaim_clean = clean_klaim(df_klaim)

    # ---- FASE 4: MERGING ----
    df_merged = merge_datasets(df_polis_clean, df_klaim_clean)

    # ---- FASE 5: FEATURE ENGINEERING ----
    df_featured = run_feature_engineering(df_merged)

    # ---- FASE 6: ENCODING ----
    df_encoded = encode_categorical_features(df_featured)

    # ---- FASE 7: NORMALISASI ----
    df_scaled = normalize_numeric_features(df_encoded)

    # ---- FASE 8: VALIDASI DAN EXPORT ----
    final_validation(df_scaled)
    df_final = export_prepared_data(df_scaled, PATH_OUTPUT)

    print(f"\n{'='*60}")
    print(" PIPELINE SELESAI")
    print(f" Output: {PATH_OUTPUT}")
    print(f"{'='*60}\n")

    return df_final


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    df_prepared = run_pipeline()
