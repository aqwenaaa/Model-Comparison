# 🛡️ AXA-PRISM: Predictive Risk Intelligence & Strategic Mitigation

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

Sistem Pendukung Keputusan (SPK) berbasis kecerdasan buatan untuk mitigasi risiko klaim asuransi kesehatan AXA melalui pendekatan **Hybrid Intelligence**.

---

## 👥 Tim Proyek PBL

Proyek ini dikembangkan oleh Kelompok PBL Mahasiswa Sistem Informasi Bisnis:

| Peran | Nama |
| :--- | :--- |
| **Project Manager** | **Aqueena Regita Hapsari** |
| **Anggota Tim** | Aidatul Rosida |
| | Faiza Anathasya Eka Falen |
| | Nervalina Adzra Nora Aqilla |
| | Renald Agustinus |

---

## 📌 Latar Belakang Masalah
Terjadi peningkatan klaim asuransi kesehatan individu sebesar **25.5% YoY (Januari – Juni 2025)** dibandingkan periode yang sama pada tahun 2024. Peningkatan ini berdampak langsung pada penyesuaian premi yang berisiko membuat produk asuransi menjadi tidak terjangkau. 

**AXA-PRISM** hadir untuk melakukan analisa berbasis data guna mendeteksi faktor pengaruh klaim serta memberikan inisiatif seleksi risiko dan deteksi dini.

---

## 🧠 Arsitektur Kecerdasan Hibrida
Sistem ini menggabungkan model statistik modern dengan sistem berbasis pengetahuan tradisional untuk memastikan keputusan yang transparan dan akurat.

### 1. Core AI Engine (Machine Learning)
* **Regression Model:** Menghitung **Expected Cost** sebagai standar biaya statistik berdasarkan profil nasabah.
* **Isolation Forest:** Mendeteksi anomali pada deviasi biaya (Actual vs Expected).
* **K-Means Clustering:** Melakukan segmentasi risiko nasabah untuk menemukan akar penyebab kebocoran biaya.

### 2. Knowledge-Based Engine (Comparator)
Digunakan sebagai pembanding akurasi dan validasi logika bisnis:
* **Forward & Backward Chaining:** Validasi kelayakan klaim berdasarkan aturan polis.
* **Teorema Bayes:** Menghitung probabilitas posterior risiko tinggi berdasarkan lokasi dan diagnosa.
* **Certainty Factors:** Mengukur tingkat keyakinan pada temuan anomali audit medis.

---

## 🛠️ Metodologi Proyek: CRISP-DM
Sistem dikembangkan mengikuti tahapan standar industri:
1.  **Business Understanding:** Identifikasi isu inflasi medis 25.5%.
2.  **Data Understanding:** Audit kualitas data dan visualisasi distribusi biaya.
3.  **Data Preparation:** *Merging*, *Feature Engineering*, dan penanganan *outlier* (Flagging).
4.  **Modeling:** Implementasi model regresi, anomali, dan sistem pakar tradisional.
5.  **Evaluation:** Komparasi akurasi antara model AI modern dan model tradisional.

---

## 👤 Dashboard Berbasis Peran (User Roles)
Sistem membagi akses untuk memastikan tata kelola yang baik (Governance):

* **Data Operator:** Mengelola *upload* data dan validasi integritas *ingestion*.
* **Risk Analyst:** Menganalisa deviasi biaya dan mencari penyebab kebocoran (*cost leakage*).
* **Medical Auditor:** Menindaklanjuti klaim anomali melalui *second opinion* atau audit rumah sakit.
* **Strategic Manager:** Menentukan kebijakan penyesuaian premi dan strategi mitigasi jangka panjang.

---

## 📈 Alur Pengambilan Keputusan
1.  **Analisis Deviasi:** Membandingkan biaya asli dengan ekspektasi model regresi.
2.  **Identifikasi Penyebab:** Menggunakan *clustering* untuk melihat apakah deviasi disebabkan oleh RS tertentu atau pola penyakit.
3.  **Percentile Ranking:** Menentukan **Tier 1 (Critical)** bagi nasabah dengan deviasi tertinggi (Top 5%).
4.  **Rekomendasi Strategis:** Menghasilkan saran tindakan otomatis seperti *"Naikkan premi 15% pada cluster X"* atau *"Audit RS Y"*.

---

> ### 🚀 Visi Proyek
> "Menciptakan ekosistem asuransi yang berkelanjutan dengan menekan inefisiensi biaya melalui transparansi data dan kecerdasan buatan."