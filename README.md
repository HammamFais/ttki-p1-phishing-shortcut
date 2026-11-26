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

## Riwayat revisi RQ

Proposal awal kelompok memakai RQ dari buku petunjuk (Bab 3.1): pengaruh fitur URL-only dan *domain-grouped split* terhadap F1, ROC-AUC, dan waktu inferensi. Audit data kemudian menemukan bahwa semua URL sah di PhiUSIIL mengikuti satu templat (https, diawali `www.`, tanpa path, `URLSimilarityIndex = 100`), dan bahwa split per hostname hampir sama dengan *random split* karena hampir setiap hostname hanya muncul sekali. RQ lalu direvisi menjadi RQ1 dan RQ2 di atas, sesuai buku petunjuk Bab 4.2 no. 7 (revisi RQ bila temuan awal mengubah persoalan).
