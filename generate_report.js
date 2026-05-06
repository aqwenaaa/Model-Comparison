const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
  TableOfContents
} = require('docx');
const fs = require('fs');

// Color palette
const BLUE_DARK = "1F3864";
const BLUE_MED = "2E75B6";
const BLUE_LIGHT = "D6E4F7";
const GRAY_LIGHT = "F2F2F2";
const WHITE = "FFFFFF";
const BLACK = "000000";
const GREEN = "375623";
const GREEN_LIGHT = "E2EFDA";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 180 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Times New Roman", color: BLUE_DARK })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Times New Roman", color: BLUE_MED })]
  });
}

function heading3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Times New Roman", color: BLUE_MED })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 360 },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, size: 24, font: "Times New Roman", ...opts })]
  });
}

function paraRuns(runs) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 360 },
    alignment: AlignmentType.JUSTIFIED,
    children: runs.map(r => new TextRun({ size: 24, font: "Times New Roman", ...r }))
  });
}

function emptyLine() {
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun("")] });
}

function bulletItem(text, opts = {}) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 60, after: 60, line: 340 },
    children: [new TextRun({ text, size: 24, font: "Times New Roman", ...opts })]
  });
}

function headerCell(text, widthDXA, shade = BLUE_MED) {
  return new TableCell({
    borders,
    width: { size: widthDXA, type: WidthType.DXA },
    shading: { fill: shade, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, size: 20, font: "Times New Roman", color: WHITE })]
    })]
  });
}

function dataCell(text, widthDXA, shade = WHITE, align = AlignmentType.CENTER, bold = false) {
  return new TableCell({
    borders,
    width: { size: widthDXA, type: WidthType.DXA },
    shading: { fill: shade, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text: String(text), size: 20, font: "Times New Roman", bold, color: BLACK })]
    })]
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ===== TABLE: Kriteria Bobot =====
function tabelKriteria() {
  const colWidths = [1200, 2200, 1400, 1200, 3360];
  const rows = [
    new TableRow({ children: [
      headerCell("Kode", colWidths[0]),
      headerCell("Nama Kriteria", colWidths[1]),
      headerCell("Tipe", colWidths[2]),
      headerCell("Bobot", colWidths[3]),
      headerCell("Deskripsi", colWidths[4]),
    ], tableHeader: true }),
    ...[ 
      ["C1","Total Klaim","Cost","0.25","Nilai total klaim per polis (semakin kecil semakin baik)"],
      ["C2","Frekuensi Klaim","Cost","0.20","Jumlah klaim yang diajukan nasabah"],
      ["C3","Durasi Rawat","Cost","0.15","Rata-rata lama hari perawatan per klaim"],
      ["C4","Usia Pasien","Cost","0.15","Usia rata-rata pasien pada polis tersebut"],
      ["C5","Lama Polis","Benefit","0.15","Lama polis aktif (semakin lama semakin baik)"],
      ["C6","Rasio Approval","Benefit","0.10","Persentase klaim yang disetujui atas total klaim"],
    ].map((row, i) => new TableRow({
      children: [
        dataCell(row[0], colWidths[0], i % 2 === 0 ? GRAY_LIGHT : WHITE),
        dataCell(row[1], colWidths[1], i % 2 === 0 ? GRAY_LIGHT : WHITE, AlignmentType.LEFT),
        dataCell(row[2], colWidths[2], i % 2 === 0 ? GRAY_LIGHT : WHITE, AlignmentType.CENTER,
          row[2] === "Benefit"),
        dataCell(row[3], colWidths[3], i % 2 === 0 ? GRAY_LIGHT : WHITE),
        dataCell(row[4], colWidths[4], i % 2 === 0 ? GRAY_LIGHT : WHITE, AlignmentType.LEFT),
      ]
    }))
  ];
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ===== TABLE: Top 5 Borda =====
function tabelTop5() {
  const colWidths = [1200, 1600, 1600, 1560, 1600, 1800];
  const rows = [
    new TableRow({ children: [
      headerCell("Alternatif", colWidths[0]),
      headerCell("Nomor Polis", colWidths[1]),
      headerCell("Borda Score", colWidths[2]),
      headerCell("Avg Rank", colWidths[3]),
      headerCell("Ranking Borda", colWidths[4]),
      headerCell("Keterangan", colWidths[5]),
    ], tableHeader: true }),
    ...[ 
      ["A04","POL-3314","207","1.25","1","Terbaik - konsisten di semua metode"],
      ["A06","POL-0106","196","4.00","2","Performa sangat baik di SAW & AHP"],
      ["A11","POL-0058","195","4.25","3","Unggul di EDAS, baik di TOPSIS"],
      ["A03","POL-1625","195","4.25","3","Sangat stabil di seluruh metode"],
      ["A07","POL-1707","185","6.75","5","Konsisten di posisi menengah-atas"],
    ].map((row, i) => new TableRow({
      children: row.map((v, j) => dataCell(v, colWidths[j],
        i === 0 ? GREEN_LIGHT : (i % 2 === 0 ? GRAY_LIGHT : WHITE),
        j === 5 ? AlignmentType.LEFT : AlignmentType.CENTER,
        i === 0 && j === 0))
    }))
  ];
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ===== TABLE: Ranking Perbandingan =====
function tabelPerbandingan() {
  const colWidths = [900, 1300, 1440, 1440, 1440, 1440, 1360];
  const rows = [
    new TableRow({ children: [
      headerCell("Alt.", colWidths[0]),
      headerCell("Polis", colWidths[1]),
      headerCell("Rank SAW", colWidths[2]),
      headerCell("Rank EDAS", colWidths[3]),
      headerCell("Rank TOPSIS", colWidths[4]),
      headerCell("Rank AHP", colWidths[5]),
      headerCell("Avg Rank", colWidths[6]),
    ], tableHeader: true }),
    ...[
      ["A04","POL-3314","1","1","2","1","1.25"],
      ["A06","POL-0106","2","3","9","2","4.00"],
      ["A11","POL-0058","6","2","4","5","4.25"],
      ["A03","POL-1625","5","5","3","4","4.25"],
      ["A07","POL-1707","10","6","5","6","6.75"],
      ["A13","POL-0564","3","9","13","3","7.00"],
      ["A02","POL-3030","4","8","10","7","7.25"],
      ["A10","POL-0400","12","4","1","13","7.50"],
      ["A15","POL-3114","9","12","8","10","9.75"],
      ["A08","POL-3008","16","7","6","16","11.25"],
    ].map((row, i) => new TableRow({
      children: row.map((v, j) => dataCell(v, colWidths[j],
        i % 2 === 0 ? GRAY_LIGHT : WHITE,
        AlignmentType.CENTER))
    }))
  ];
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ===== TABLE: Korelasi Spearman =====
function tabelKorelasi() {
  const colWidths = [2100, 1815, 1815, 1815, 1815];
  const getShade = (val) => {
    const f = parseFloat(val);
    if (f >= 0.9) return "1F5C1F";
    if (f >= 0.8) return "2E8B2E";
    if (f >= 0.7) return "82C682";
    return GRAY_LIGHT;
  };
  const data = [
    ["Metode","Ranking_SAW","Ranking_EDAS","Ranking_TOPSIS","Ranking_AHP"],
    ["Ranking_SAW","1.0000","0.7585","0.6549","0.8727"],
    ["Ranking_EDAS","0.7585","1.0000","0.9174","0.8234"],
    ["Ranking_TOPSIS","0.6549","0.9174","1.0000","0.6832"],
    ["Ranking_AHP","0.8727","0.8234","0.6832","1.0000"],
  ];
  const rows = data.map((row, i) => new TableRow({
    children: row.map((v, j) => {
      if (i === 0) return headerCell(v, colWidths[j]);
      if (j === 0) return dataCell(v, colWidths[j], BLUE_LIGHT, AlignmentType.LEFT, true);
      const shade = i === j ? BLUE_MED : getShade(v);
      const txtColor = (i === j || parseFloat(v) >= 0.8) ? WHITE : BLACK;
      return new TableCell({
        borders,
        width: { size: colWidths[j], type: WidthType.DXA },
        shading: { fill: shade, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: v, bold: i === j, size: 20, font: "Times New Roman", color: txtColor })]
        })]
      });
    })
  }));
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ===== TABLE: AHP Consistency =====
function tabelAHP() {
  const colWidths = [2200, 2000, 2000, 3160];
  const rows = [
    new TableRow({ children: [
      headerCell("Parameter", colWidths[0]),
      headerCell("Nilai", colWidths[1]),
      headerCell("Ambang Batas", colWidths[2]),
      headerCell("Interpretasi", colWidths[3]),
    ], tableHeader: true }),
    ...[
      ["Consistency Ratio (CR)","0.0059","< 0.1","VALID - Matriks perbandingan konsisten"],
      ["Principal Eigenvalue (λmax)","~6.035","Mendekati n=6","Perbedaan dari ideal sangat kecil"],
      ["Consistency Index (CI)","~0.007","≤ 0.1","Tingkat inkonsistensi sangat rendah"],
      ["Random Index (RI)","1.24","Standar n=6","Nilai referensi Saaty untuk 6 kriteria"],
    ].map((row, i) => new TableRow({
      children: row.map((v, j) => dataCell(v, colWidths[j],
        i % 2 === 0 ? GRAY_LIGHT : WHITE,
        j === 0 ? AlignmentType.LEFT : (j === 3 ? AlignmentType.LEFT : AlignmentType.CENTER)))
    }))
  ];
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ===== DOCUMENT BUILD =====
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Times New Roman", color: BLUE_DARK },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Times New Roman", color: BLUE_MED },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE_MED, space: 1 } },
            alignment: AlignmentType.RIGHT,
            spacing: { after: 120 },
            children: [
              new TextRun({ text: "Laporan Analisis MCDM - Sistem Asuransi AXA | CRISP-DM Framework", size: 18, font: "Times New Roman", color: "888888" })
            ]
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 6, color: BLUE_MED, space: 1 } },
            spacing: { before: 120 },
            children: [
              new TextRun({ text: "Halaman ", size: 18, font: "Times New Roman", color: "888888" }),
              new PageNumber(),
              new TextRun({ text: " | Analisis MCDM: SAW, EDAS, TOPSIS, AHP | Tanggal: 5 Mei 2026", size: 18, font: "Times New Roman", color: "888888" }),
            ]
          })
        ]
      })
    },
    children: [
      // ============ COVER ============
      new Paragraph({ spacing: { before: 1440, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "LAPORAN FINAL ANALISIS", size: 48, bold: true, font: "Times New Roman", color: BLUE_DARK })] }),
      new Paragraph({ spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Multi-Criteria Decision Making (MCDM)", size: 40, bold: true, font: "Times New Roman", color: BLUE_MED })] }),
      new Paragraph({ spacing: { before: 0, after: 600 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Sistem Evaluasi Risiko Polis Asuransi AXA", size: 36, font: "Times New Roman", color: "555555" })] }),

      new Paragraph({ spacing: { before: 0, after: 100 }, alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 12, color: BLUE_MED, space: 1 }, bottom: { style: BorderStyle.SINGLE, size: 4, color: BLUE_MED, space: 4 } },
        children: [new TextRun({ text: "", size: 24 })] }),
      emptyLine(),

      new Paragraph({ spacing: { before: 80, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Framework: CRISP-DM  |  Metode: SAW, EDAS, TOPSIS, AHP", size: 24, font: "Times New Roman", color: "555555" })] }),
      new Paragraph({ spacing: { before: 80, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Tanggal Analisis: 5 Mei 2026  |  Total Rekaman: 4.627 Klaim  |  Alternatif Dianalisis: 52 Polis", size: 22, font: "Times New Roman", color: "777777" })] }),
      emptyLine(),
      new Paragraph({ spacing: { before: 80, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Kuis 2 - Sistem Berbasis Pengetahuan", size: 24, bold: true, font: "Times New Roman", color: BLUE_DARK })] }),

      pageBreak(),

      // ============ BAB I ============
      heading1("BAB I: PENDAHULUAN DAN PENYIAPAN DATA (DATA PREPARATION)"),
      heading2("1.1 Latar Belakang dan Tujuan Pemodelan"),

      para("Industri asuransi kesehatan menghadapi tantangan signifikan dalam mengelola risiko klaim yang bervariasi secara luas antar pemegang polis. Nilai klaim, frekuensi pengajuan, durasi perawatan, hingga profil demografis nasabah merupakan faktor-faktor kompleks yang tidak dapat dievaluasi secara independen. Diperlukan suatu kerangka pengambilan keputusan yang mampu mengintegrasikan berbagai kriteria secara simultan, objektif, dan terukur."),
      emptyLine(),
      para("Penelitian ini mengimplementasikan empat metode Multi-Criteria Decision Making (MCDM) — yaitu Simple Additive Weighting (SAW), Evaluation based on Distance from Average Solution (EDAS), Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS), dan Analytic Hierarchy Process (AHP) — untuk mengevaluasi dan memprioritaskan risiko dari 52 polis asuransi yang dipilih dari dataset AXA. Analisis dilaksanakan dengan mengikuti tahapan CRISP-DM (Cross-Industry Standard Process for Data Mining) sehingga proses bersifat terstruktur, dapat direplikasi, dan berorientasi pada kebutuhan bisnis."),
      emptyLine(),
      para("Tujuan utama pemodelan ini adalah: (1) membandingkan performa dan konsistensi keempat algoritma MCDM dalam menghasilkan urutan prioritas polis; (2) mengidentifikasi alternatif polis terbaik berdasarkan agregasi hasil keempat metode melalui metode Borda Count; dan (3) merekomendasikan metode MCDM yang paling sesuai untuk diintegrasikan ke dalam core sistem deteksi anomali klaim AXA-PRISM."),

      emptyLine(),
      heading2("1.2 Deskripsi Data dan Statistik Awal"),

      para("Dataset yang digunakan bersumber dari sistem internal asuransi AXA dengan rincian sebagai berikut:"),
      emptyLine(),
      bulletItem("Total rekaman klaim: 4.627 transaksi klaim"),
      bulletItem("Total polis unik yang teridentifikasi: 4.096 polis"),
      bulletItem("Alternatif yang dianalisis dalam matriks keputusan MCDM: 52 polis terpilih"),
      bulletItem("Periode analisis: Sesuai data historis yang tersedia dalam sistem AXA"),
      emptyLine(),
      para("Dari 4.096 polis yang ada, proses preprocessing menghasilkan 52 alternatif yang representatif dan memiliki kelengkapan data pada seluruh enam kriteria yang ditetapkan. Pemilihan 52 alternatif ini memastikan bahwa matriks keputusan MCDM dapat diisi secara penuh tanpa imputasi nilai yang dapat mempengaruhi integritas hasil analisis."),

      emptyLine(),
      heading2("1.3 Kriteria dan Bobot MCDM"),

      para("Berdasarkan konsultasi dengan pakar domain asuransi dan kajian literatur manajemen risiko klaim, ditetapkan enam kriteria evaluasi beserta bobot kepentingannya. Penentuan bobot menggunakan metode Analytic Hierarchy Process (AHP) dengan validasi Consistency Ratio (CR = 0,0059 < 0,1), yang membuktikan bahwa penilaian bobot bersifat konsisten dan dapat dipertanggungjawabkan secara ilmiah."),
      emptyLine(),

      tabelKriteria(),
      emptyLine(),

      para("Distribusi bobot mencerminkan prioritas bisnis AXA, di mana aspek finansial (Total Klaim, bobot 0,25) mendominasi karena langsung berdampak pada profitabilitas perusahaan. Kriteria Frekuensi Klaim (0,20) menempati posisi kedua sebagai indikator kerentanan nasabah. Tiga kriteria dengan bobot setara (0,15 masing-masing) — Durasi Rawat, Usia Pasien, dan Lama Polis — mencerminkan bahwa faktor operasional dan loyalitas nasabah mendapat perhatian yang seimbang. Rasio Approval (0,10) sebagai kriteria benefit dengan bobot terkecil menunjukkan bahwa performa persetujuan klaim berkontribusi namun tidak dominan dalam menentukan risiko polis."),

      pageBreak(),

      // ============ BAB II ============
      heading1("BAB II: PEMBAHASAN DAN PROSES METODE (STEP-BY-STEP EXPLANATION)"),
      heading2("2.1 Metode Simple Additive Weighting (SAW)"),

      para("SAW merupakan metode MCDM paling fundamental yang bekerja dengan menormalkan nilai setiap kriteria dan kemudian mengalikannya dengan bobot masing-masing. Proses normalisasi membedakan antara kriteria Cost dan Benefit: untuk kriteria Cost (C1–C4), nilai dinormalisasi dengan formula rij = min(xij)/xij, sehingga polis dengan nilai lebih kecil mendapat skor normalisasi lebih tinggi. Sebaliknya, untuk kriteria Benefit (C5–C6), normalisasi menggunakan rij = xij/max(xij)."),
      emptyLine(),
      para("Nilai Preferensi SAW kemudian dihitung sebagai jumlah tertimbang dari nilai ternormalisasi: Vi = Σ(wj × rij). Berdasarkan hasil komputasi yang tersimpan dalam file hasil_saw.csv, alternatif A04 (POL-3314) meraih nilai preferensi tertinggi sebesar 0,7898, diikuti oleh A06 (POL-0106) dengan nilai 0,7149, dan A13 (POL-0564) dengan nilai 0,6615. Ketiga polis ini unggul karena memiliki kombinasi Total Klaim rendah dan Frekuensi Klaim rendah — dua kriteria dengan bobot terbesar (0,25 dan 0,20) — sehingga mendominasi hasil akhir SAW."),
      emptyLine(),

      paraRuns([
        { text: "Catatan kritis: ", bold: true },
        { text: "SAW menunjukkan sensitivitas tinggi terhadap nilai ekstrem. Alternatif A17 (POL-3328), misalnya, memiliki nilai SAW sangat rendah (0,2490, peringkat ke-40) meskipun memiliki EDAS score yang relatif tinggi (0,7879, peringkat ke-19). Hal ini disebabkan karena A17 kemungkinan memiliki nilai Total Klaim atau Frekuensi Klaim yang ekstrem tinggi, sehingga setelah dinormalisasi menghasilkan skor yang sangat kecil dan menurunkan nilai preferensi secara signifikan. Fenomena ini merupakan kelemahan inheren SAW yang perlu diperhatikan dalam konteks data asuransi dengan distribusi klaim yang skewed." }
      ]),

      emptyLine(),
      heading2("2.2 Metode Evaluation Based on Distance from Average Solution (EDAS)"),

      para("EDAS merupakan metode yang relatif lebih robust terhadap outlier dibandingkan SAW dan TOPSIS. Alih-alih membandingkan setiap alternatif terhadap solusi ideal positif dan negatif, EDAS menggunakan rata-rata dari seluruh alternatif (Average Solution/AV) sebagai titik acuan evaluasi."),
      emptyLine(),
      para("Langkah pertama dalam EDAS adalah menghitung Average Solution (AV) untuk setiap kriteria, yaitu rata-rata aritmetika dari seluruh 52 alternatif. Selanjutnya, untuk setiap pasangan alternatif-kriteria dihitung dua jarak: Positive Distance from Average (PDA) yang mengukur seberapa jauh alternatif berada di atas rata-rata dalam arah yang menguntungkan, dan Negative Distance from Average (NDA) yang mengukur seberapa jauh alternatif berada di bawah rata-rata dalam arah yang merugikan."),
      emptyLine(),
      para("Appraisal Score (AS) EDAS kemudian dihitung dengan memadukan skor PDA dan NDA yang telah dinormalisasi, sehingga alternatif dengan PDA tinggi dan NDA rendah akan mendapatkan AS mendekati 1,0. Berdasarkan data dalam hasil_edas.csv, A04 (POL-3314) mencapai Appraisal Score tertinggi sebesar 0,9941 — mendekati nilai sempurna — yang menandakan bahwa polis ini berada jauh di atas rata-rata pada kriteria-kriteria Cost dan sekaligus di atas rata-rata pada kriteria Benefit. A11 (POL-0058) menyusul di posisi kedua dengan AS sebesar 0,9820, sedangkan A06 di posisi ketiga dengan AS 0,9457."),
      emptyLine(),
      para("Keunggulan EDAS terletak pada kemampuannya mengevaluasi kinerja relatif terhadap rata-rata populasi, bukan terhadap nilai ekstrem. Ini membuat EDAS lebih stabil dan tidak terdistorsi oleh outlier — sifat yang sangat relevan untuk dataset klaim asuransi yang lazimnya memiliki distribusi right-skewed dengan beberapa nilai klaim yang sangat besar."),

      emptyLine(),
      heading2("2.3 Metode Technique for Order Preference by Similarity to Ideal Solution (TOPSIS)"),

      para("TOPSIS mengevaluasi setiap alternatif berdasarkan jaraknya terhadap dua titik ekstrem: Solusi Ideal Positif (A+) yang merepresentasikan nilai terbaik pada setiap kriteria, dan Solusi Ideal Negatif (A-) yang merepresentasikan nilai terburuk. Alternatif terbaik menurut TOPSIS adalah yang memiliki jarak terpendek dari A+ sekaligus jarak terjauh dari A-."),
      emptyLine(),
      para("Proses TOPSIS dimulai dengan normalisasi matriks keputusan menggunakan metode vektor (rij = xij / √Σxij²), dilanjutkan dengan pembobotan matriks normalisasi (vij = wj × rij), dan kemudian identifikasi A+ dan A- dari setiap kolom. Jarak setiap alternatif terhadap A+ (D+) dan A- (D-) dihitung menggunakan jarak Euclidean, dan nilai preferensi akhir diperoleh dari: Ci = D- / (D+ + D-)."),
      emptyLine(),
      para("Berdasarkan data hasil_topsis.csv, alternatif A10 (POL-0400) menempati peringkat pertama TOPSIS dengan nilai preferensi 0,9429, D+ = 0,01258, dan D- = 0,20755. Nilai D+ yang sangat kecil menunjukkan bahwa A10 berada sangat dekat dengan Solusi Ideal Positif, sementara D- yang besar mengonfirmasi jaraknya yang jauh dari Solusi Ideal Negatif. Menariknya, A10 hanya berada di peringkat ke-12 dalam SAW dan ke-13 dalam AHP, mengindikasikan bahwa A10 memiliki keunggulan komparatif yang kuat pada kriteria-kriteria tertentu yang diuntungkan oleh metode jarak Euclidean TOPSIS, namun tidak terlalu dominan secara keseluruhan ketika dievaluasi dengan bobot langsung."),
      emptyLine(),
      para("A04 (POL-3314) menempati peringkat kedua TOPSIS dengan D+ = 0,01536 dan D- = 0,21198, nilai preferensi 0,9324. Selisih tipis antara A10 dan A04 pada TOPSIS (0,9429 vs 0,9324) mencerminkan bahwa kedua polis ini sama-sama memiliki profil risiko yang sangat baik, dengan perbedaan tipis pada distribusi kinerja antar kriteria."),

      emptyLine(),
      heading2("2.4 Metode Analytic Hierarchy Process (AHP)"),

      para("AHP merupakan metode yang paling terstruktur secara matematis karena melibatkan proses perbandingan berpasangan (pairwise comparison) antar kriteria untuk menentukan bobot secara ilmiah. Bobot yang dihasilkan AHP bukan ditentukan secara langsung oleh pengambil keputusan, melainkan diturunkan dari matriks perbandingan berpasangan yang dibangun berdasarkan skala Saaty (1–9)."),
      emptyLine(),
      para("Syarat validitas AHP adalah nilai Consistency Ratio (CR) yang harus lebih kecil dari 0,1. Berdasarkan laporan analisis, CR yang diperoleh adalah 0,0059 — jauh di bawah ambang batas 0,1. Nilai CR yang sangat kecil ini membuktikan bahwa penilaian perbandingan berpasangan antar kriteria bersifat sangat konsisten dan tidak mengandung kontradiksi logis yang signifikan. Dengan CR = 0,0059, bobot yang dihasilkan AHP dapat dipercaya sebagai representasi yang valid dari preferensi relatif antar kriteria."),
      emptyLine(),

      tabelAHP(),
      emptyLine(),

      para("Bobot akhir yang dihasilkan AHP selaras dengan bobot yang ditetapkan: Total Klaim (0,25), Frekuensi Klaim (0,20), Durasi Rawat (0,15), Usia Pasien (0,15), Lama Polis (0,15), dan Rasio Approval (0,10). Berdasarkan hasil_ahp.csv, nilai preferensi AHP untuk A04 adalah 0,7995 (peringkat 1), A06 sebesar 0,7467 (peringkat 2), dan A13 sebesar 0,6723 (peringkat 3). Distribusi nilai preferensi AHP memiliki rata-rata 0,3978 dan median 0,3792, menunjukkan distribusi yang sedikit right-skewed akibat keunggulan signifikan beberapa alternatif teratas."),

      pageBreak(),

      // ============ BAB III ============
      heading1("BAB III: ANALISIS PERBANDINGAN METODE (COMPARATIVE ANALYSIS)"),
      heading2("3.1 Tabel Perbandingan Ranking Lintas Metode"),

      para("Tabel berikut menyajikan perbandingan peringkat 10 alternatif terbaik berdasarkan rata-rata ranking (Avg Rank) dari keempat metode MCDM:"),
      emptyLine(),

      tabelPerbandingan(),
      emptyLine(),

      para("Dari tabel di atas, terlihat bahwa A04 merupakan satu-satunya alternatif yang memperoleh peringkat 1 di tiga dari empat metode (SAW, EDAS, AHP) dan peringkat 2 di TOPSIS, menjadikannya alternatif dengan konsistensi tertinggi dengan Avg Rank = 1,25. Sebaliknya, A10 menunjukkan fluktuasi ranking yang cukup besar: peringkat 1 di TOPSIS, peringkat 4 di EDAS, namun turun ke peringkat 12 di SAW dan peringkat 13 di AHP (Avg Rank = 7,50)."),

      emptyLine(),
      heading2("3.2 Matriks Korelasi Spearman antar Metode"),

      para("Untuk mengukur tingkat kesepakatan antar metode secara kuantitatif, digunakan korelasi Spearman (rank correlation). Korelasi ini mengukur seberapa konsisten dua metode dalam mengurut alternatif secara relatif, terlepas dari nilai absolutnya."),
      emptyLine(),

      tabelKorelasi(),
      emptyLine(),

      para("Korelasi Spearman rata-rata antar semua pasangan metode adalah 0,7850, yang mengindikasikan tingkat kesepakatan yang kuat secara keseluruhan. Analisis pasangan-pasangan spesifik mengungkapkan pola yang informatif:"),
      emptyLine(),
      bulletItem("EDAS vs TOPSIS (0,9174): Pasangan ini memiliki korelasi tertinggi, menunjukkan bahwa kedua metode memberikan hasil ranking yang hampir identik. Hal ini dapat dijelaskan secara teoritis karena keduanya memiliki sifat yang sama: EDAS menggunakan rata-rata populasi sebagai referensi, sementara TOPSIS menggunakan jarak ke ideal. Kedua pendekatan ini menghasilkan evaluasi yang lebih nuanced dan tidak terlalu sensitif terhadap nilai ekstrem pada satu kriteria saja."),
      bulletItem("SAW vs AHP (0,8727): Korelasi yang sangat tinggi ini logis karena AHP pada dasarnya merupakan pengembangan dari SAW dengan penambahan proses pairwise comparison untuk menentukan bobot. Ketika bobot telah ditentukan, mekanisme penghitungan nilai preferensi AHP mirip dengan SAW, sehingga menghasilkan ranking yang serupa."),
      bulletItem("SAW vs TOPSIS (0,6549): Pasangan dengan korelasi terendah. Perbedaan ini mencerminkan perbedaan fundamental dalam mekanisme: SAW menggunakan penjumlahan nilai bobot ternormalisasi (sensitif terhadap kinerja rata-rata di semua kriteria), sementara TOPSIS mengedepankan jarak Euclidean ke titik ideal (sensitif terhadap profil kinerja dimensional). Alternatif yang unggul di beberapa kriteria secara ekstrem dapat diuntungkan oleh TOPSIS meski rata-rata SAW-nya tidak setinggi itu."),
      bulletItem("SAW vs EDAS (0,7585) dan AHP vs EDAS (0,8234): Korelasi moderat-tinggi, menunjukkan bahwa EDAS memiliki posisi \"tengah\" di antara metode berbasis rata-rata langsung (SAW/AHP) dan metode berbasis jarak (TOPSIS)."),

      emptyLine(),
      heading2("3.3 Analisis Persentase Kemiripan dan Perbedaan"),

      para("Berdasarkan laporan analisis, akurasi exact match antar metode adalah 0,0%, artinya tidak ada satu pun alternatif yang memiliki peringkat persis sama di keempat metode sekaligus. Ini adalah temuan yang wajar mengingat keempat metode memiliki mekanisme matematis yang berbeda. Namun dengan toleransi ±5 peringkat, akurasi kesesuaian meningkat menjadi 15,4%, dan dengan toleransi ±10 akurasi mencapai 42,3%."),
      emptyLine(),
      para("Persentase kemiripan global, yang diukur sebagai akurasi keseluruhan berdasarkan korelasi Spearman rata-rata 0,7850, dapat diinterpretasikan sebagai tingkat konsensus 78,5% antar metode. Artinya, dari perspektif urutan relatif, keempat metode \"sepakat\" pada sekitar 78,5% dari penilaian mereka."),
      emptyLine(),
      para("Sementara itu, persentase perbedaan sebesar ~21,5% dapat dijelaskan melalui beberapa faktor teoritis dan empiris:"),
      emptyLine(),
      bulletItem("Sensitivitas SAW terhadap outlier: SAW rentan terhadap nilai ekstrem karena normalisasi min/max langsung memperbesar perbedaan relatif pada distribusi yang skewed. Dalam dataset klaim asuransi, polis dengan satu klaim bernilai sangat besar dapat memperoleh nilai normalisasi yang sangat rendah di SAW, bahkan jika kinerja di kriteria lain cukup baik."),
      bulletItem("Sifat kompensasi TOPSIS: TOPSIS secara eksplisit mempertimbangkan trade-off antar dimensi melalui jarak Euclidean multidimensional. Polis yang sangat unggul pada satu atau dua kriteria dapat memiliki D+ yang sangat kecil sehingga menempati peringkat tinggi di TOPSIS, meski nilai SAW atau AHP-nya biasa saja."),
      bulletItem("Referensi rata-rata EDAS: EDAS mengukur kinerja relatif terhadap rata-rata populasi, bukan nilai ekstrem. Ini membuat EDAS kurang terpengaruh oleh polis-polis dengan nilai sangat ekstrem (baik ekstrem tinggi maupun rendah), sehingga menghasilkan distribusi ranking yang lebih merata."),
      bulletItem("Bobot AHP berbasis pairwise: Meskipun bobot akhir AHP identik dengan yang digunakan SAW, proses turunan bobot melalui matriks perbandingan berpasangan dan normalisasi eigenvector dapat menghasilkan perbedaan kecil dalam presisi bobot yang, ketika dikalikan dengan 52 alternatif, mengakumulasi perbedaan ranking pada alternatif-alternatif di tengah distribusi."),

      emptyLine(),
      heading2("3.4 Analisis Variabilitas dan Stabilitas Ranking"),

      para("Standar deviasi ranking rata-rata (mean Std_Rank) sebesar 5,98 mengindikasikan bahwa secara umum, setiap alternatif mengalami fluktuasi ranking sekitar ±6 posisi di antara keempat metode. Alternatif dengan standar deviasi rendah (seperti A04 dengan Std_Rank = 0,5 dan A03 dengan Std_Rank = 0,96) adalah alternatif yang paling konsisten dan dapat diandalkan untuk direkomendasikan, karena semua metode sepakat bahwa polis-polis ini memiliki risiko rendah."),
      emptyLine(),
      para("Sebaliknya, alternatif seperti A28 (Std_Rank = 8,34) dan A40 (Std_Rank = 15,78) menunjukkan volatilitas tinggi — artinya, penilaian risiko polis-polis ini sangat bergantung pada pilihan metode MCDM yang digunakan. Polis A40 menempati peringkat ke-7 di SAW namun anjlok ke peringkat ke-40 di TOPSIS dan ke-32 di EDAS, mencerminkan profil risiko yang ambigu dan sulit dikategorikan secara definitif."),

      pageBreak(),

      // ============ BAB IV ============
      heading1("BAB IV: KESIMPULAN DAN REKOMENDASI"),
      heading2("4.1 Kesimpulan Analisis"),

      para("Penelitian ini berhasil mengimplementasikan dan membandingkan empat metode MCDM — SAW, EDAS, TOPSIS, dan AHP — untuk mengevaluasi 52 alternatif polis asuransi AXA berdasarkan enam kriteria risiko klaim. Beberapa kesimpulan utama dapat ditarik sebagai berikut:"),
      emptyLine(),
      bulletItem("Alternatif A04 (POL-3314) merupakan polis dengan risiko terbaik secara konsisten. Dengan Borda Score tertinggi sebesar 207 dan Avg Rank 1,25, A04 menempati peringkat pertama di SAW (0,7898), EDAS (0,9941), dan AHP (0,7995), serta peringkat kedua di TOPSIS (0,9324). Konsistensi ini memberikan keyakinan tinggi bahwa POL-3314 adalah polis dengan profil risiko paling menguntungkan bagi AXA."),
      bulletItem("Keempat metode MCDM menunjukkan tingkat kesepakatan yang kuat dengan korelasi Spearman rata-rata 0,7850. Pasangan EDAS-TOPSIS memiliki korelasi tertinggi (0,9174), sedangkan SAW-TOPSIS memiliki korelasi terendah (0,6549) akibat perbedaan fundamental dalam mekanisme normalisasi dan evaluasi."),
      bulletItem("Konsistensi AHP terbukti secara matematis dengan CR = 0,0059, jauh di bawah ambang kritis 0,1, sehingga bobot yang digunakan dalam seluruh analisis dapat dianggap valid dan terpercaya."),
      bulletItem("Feature importance menunjukkan bahwa Total Klaim dan Frekuensi Klaim merupakan dua kriteria dengan pengaruh tertinggi terhadap ranking akhir, konsisten dengan bobotnya yang paling besar (0,25 dan 0,20)."),

      emptyLine(),
      heading2("4.2 Rekomendasi Metode untuk Implementasi AXA-PRISM"),

      paraRuns([
        { text: "Berdasarkan hasil analisis komparatif, metode ", bold: false },
        { text: "EDAS (Evaluation Based on Distance from Average Solution)", bold: true },
        { text: " direkomendasikan sebagai metode utama untuk diintegrasikan ke dalam core sistem deteksi anomali klaim AXA-PRISM. Rekomendasi ini didasarkan pada beberapa pertimbangan teknis dan bisnis yang kuat:", bold: false }
      ]),
      emptyLine(),
      bulletItem("Robustness terhadap outlier: EDAS menggunakan rata-rata populasi (bukan nilai ekstrem) sebagai referensi evaluasi. Dalam konteks klaim asuransi yang memiliki distribusi right-skewed dengan nilai klaim ekstrem (seperti klaim rawat inap jangka panjang atau klaim dengan komplikasi medis mahal), EDAS tidak akan \"terdistorsi\" oleh satu atau dua klaim bernilai sangat besar, tidak seperti SAW yang langsung terkena dampak normalisasi min-max."),
      bulletItem("Korelasi tertinggi dengan metode lain: EDAS memiliki korelasi Spearman 0,9174 dengan TOPSIS dan 0,8234 dengan AHP, menempatkannya sebagai metode dengan hasil paling konsisten secara lintas-metode. Dengan kata lain, EDAS cenderung menghasilkan ranking yang paling dapat \"diterima\" oleh berbagai perspektif evaluatif."),
      bulletItem("Interpretabilitas bisnis: Konsep \"jarak dari rata-rata\" dalam EDAS lebih mudah dijelaskan kepada pemangku kepentingan non-teknis dibandingkan jarak Euclidean multidimensional TOPSIS. Manajemen AXA dapat memahami bahwa polis yang berada jauh di atas rata-rata pada kriteria Cost (klaim kecil, frekuensi rendah) dan di atas rata-rata pada kriteria Benefit (polis lama, rasio approval tinggi) mendapat skor EDAS tinggi."),
      bulletItem("Performa komputasi: EDAS tidak memerlukan iterasi matriks berpasangan seperti AHP dan tidak memerlukan perhitungan jarak Euclidean kompleks seperti TOPSIS, sehingga lebih efisien secara komputasional untuk pemrosesan batch real-time dalam sistem AXA-PRISM."),
      emptyLine(),

      para("Sebagai pelengkap, direkomendasikan untuk menggunakan Borda Count dari keempat metode sebagai lapisan validasi tambahan ketika terdapat keputusan kritikal (misalnya penetapan premi tinggi atau penolakan perpanjangan polis). Borda Count memberikan konsensus yang lebih robust karena mengintegrasikan informasi dari seluruh metode, meminimalkan bias yang mungkin dimiliki satu metode tunggal."),

      emptyLine(),
      heading2("4.3 Ringkasan Eksekutif dan Rekomendasi Strategis"),

      para("Dari 52 polis yang dianalisis, lima besar polis dengan risiko terendah berdasarkan metode Borda Count adalah:"),
      emptyLine(),

      tabelTop5(),
      emptyLine(),

      para("Rekomendasi strategis untuk tim AXA-PRISM:"),
      emptyLine(),
      bulletItem("Jangka pendek: Integrasikan EDAS sebagai scoring engine utama dalam modul evaluasi risiko AXA-PRISM dengan siklus pembaruan bulanan menggunakan data klaim terbaru."),
      bulletItem("Jangka menengah: Implementasikan dashboard perbandingan keempat metode MCDM untuk monitoring divergensi. Alternatif dengan standar deviasi ranking tinggi (seperti A40 dan A28) harus mendapat perhatian khusus dari tim underwriting karena profil risikonya ambigu."),
      bulletItem("Jangka panjang: Lakukan kalibrasi ulang bobot kriteria secara berkala (minimal setahun sekali) menggunakan AHP dengan melibatkan pakar aktuaria AXA, memastikan bobot tetap mencerminkan realitas bisnis terkini dan regulasi asuransi yang berlaku."),
      bulletItem("Penanganan outlier: Tambahkan lapisan deteksi anomali berbasis statistik (misalnya Isolation Forest atau Z-Score) sebelum data masuk ke engine MCDM, untuk mengidentifikasi klaim dengan nilai ekstrem yang perlu perlakuan khusus sebelum scoring MCDM dijalankan."),

      emptyLine(),
      new Paragraph({
        spacing: { before: 200, after: 100 },
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: BLUE_MED, space: 1 } },
        children: []
      }),
      emptyLine(),
      para("Analisis ini telah membuktikan bahwa implementasi multi-metode MCDM — dengan EDAS sebagai metode utama dan Borda Count sebagai mekanisme agregasi — merupakan pendekatan yang robust, dapat dipertanggungjawabkan secara ilmiah, dan praktis untuk diterapkan dalam sistem manajemen risiko klaim asuransi AXA. Dengan CR AHP sebesar 0,0059 dan korelasi Spearman rata-rata 0,7850, kerangka MCDM yang dibangun ini memenuhi standar akademis dan kebutuhan operasional yang dipersyaratkan oleh project AXA-PRISM.", { bold: false }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('figure/Laporan_Final_MCDM_AXA.docx', buffer);
  console.log('Document created successfully!');
}).catch(err => {
  console.error('Error:', err);
  process.exit(1);
});