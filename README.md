# ttki-p1-phishing-shortcut

Proyek akhir Tata Tulis Karya Ilmiah (TTKI), topik P1: deteksi URL phishing pada dataset PhiUSIIL.
Kelompok: Hammam Hidayatullah (3124600096) dan Dimas Reza Ardhana (3124600102), Sarjana Terapan Teknik Informatika, PENS.

> README ini masih awal. Bagian cara menjalankan, hasil, dan kredit dilengkapi setelah eksperimen selesai.

## Pertanyaan penelitian

- **RQ1:** Seberapa besar kinerja deteksi phishing pada PhiUSIIL bergantung pada fitur yang mengikuti templat URL sah?
- **RQ2:** Apakah pemisahan data berdasarkan domain induk (eTLD+1) mengubah estimasi kinerja dibandingkan *stratified random split*?

## Data

Lihat [data/README.md](data/README.md). CSV tidak di-commit.

## Lingkungan

- Windows 11, Python 3.14.0
- Versi paket utama di `requirements.txt`, daftar lengkap di `environment-freeze.txt`

```bash
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Acuan dan kredit

- Protokol baseline (stratified 70/30, Logistic Regression dan Random Forest pada semua fitur numerik) mengikuti repositori [pradhyumnaag30/PhiUSIIL-Phishing-URL-Detection](https://github.com/pradhyumnaag30/PhiUSIIL-Phishing-URL-Detection) (commit `4b4d6ae`, 2025-12-04). Repositori itu tidak mencantumkan lisensi (dicek 2026-11-26), sehingga kodenya tidak disalin ke sini. Notebook `02_Baseline.ipynb` mereka dijalankan apa adanya di luar repo ini, dan protokolnya ditulis ulang di `src/baseline.py`. Perbandingan angkanya ada di `results/baseline_reference.csv` dan `results/baseline.csv`.
- `Dataset/Dataset.csv` di repositori acuan memiliki SHA-256 yang sama dengan CSV yang kami pakai (lihat `data/README.md`).

## Riwayat desain

Desain awal: F1-F3 x S1/S2 x LR/RF x 5 seed (60 run) + aturan R0, dengan S2 = `GroupShuffleSplit` per domain induk. Setelah run pertama, dua tambahan dibuat:

1. **F4 = F3 + tiga penanda templat biner** (`is_https`, `starts_www`, `no_path_query`, dihitung dari URL). F3 hanya punya 10 fitur, sedangkan F2 punya 22. F4 dipakai untuk memeriksa apakah penurunan F3 terhadap F2 disebabkan hilangnya templat atau sekadar berkurangnya jumlah fitur. Efek `F4 - F3` dan `F4 - F2` ditambahkan ke `results/stats.csv`.
2. **S2 diganti `StratifiedGroupKFold`** (`n_splits=10`, `shuffle=True`, `random_state=seed`, grup = eTLD+1). Tiga dari sepuluh fold digabung sebagai data uji (30%). Pilihan ini dibandingkan dengan `n_splits=3` dan satu fold uji (33,3%); 10 fold dengan 3 fold uji dipilih karena porsinya tepat 30%, sama dengan S1. Alasan penggantian: pada `GroupShuffleSplit` proporsi phishing di data uji bervariasi 35,8-49,0% antar seed, dan F1 pada F3 berkorelasi sekitar 0,98 dengan proporsi itu, sehingga perbandingan S1 vs S2 tercampur efek komposisi. Pemeriksaan berikutnya menunjukkan bahwa `StratifiedGroupKFold` selalu menempatkan grup terbesar di fold-fold awal (web.app, firebaseapp.com, dan weeblysite.com selalu masuk data uji bila fold 0-2 yang diambil). Karena itu tiga fold uji dipilih acak per seed dengan `numpy.random.default_rng(seed)`.
3. Hasil `GroupShuffleSplit` tidak dibuang. Hasil itu disimpan sebagai **S2g** di `results/metrics.csv` dan `results/split_report.csv`, dan diuji di `results/stats.csv` sebagai analisis sensitivitas. Angka S1 dan S2g sama dengan run pertama (matriks konfusi identik; ROC-AUC dan PR-AUC berbeda paling besar 1e-7 karena pembulatan).

Total run sekarang: 4 set fitur x 3 split x 2 model x 5 seed = 120 run, ditambah R0 untuk setiap split dan seed.

## Riwayat revisi RQ

Proposal awal kelompok memakai RQ dari buku petunjuk (Bab 3.1): pengaruh fitur URL-only dan *domain-grouped split* terhadap F1, ROC-AUC, dan waktu inferensi. Audit data kemudian menemukan bahwa semua URL sah di PhiUSIIL mengikuti satu templat (https, diawali `www.`, tanpa path, `URLSimilarityIndex = 100`), dan bahwa split per hostname hampir sama dengan *random split* karena hampir setiap hostname hanya muncul sekali. RQ lalu direvisi menjadi RQ1 dan RQ2 di atas, sesuai buku petunjuk Bab 4.2 no. 7 (revisi RQ bila temuan awal mengubah persoalan).
