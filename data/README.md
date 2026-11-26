# Data

CSV tidak disimpan di repositori ini. Unduh sendiri dari Kaggle, lalu taruh di folder induk repo (`../PhiUSIIL_Phishing_URL_Dataset.csv`) atau arahkan variabel lingkungan `PHIUSIIL_CSV` ke lokasi file.

## Sumber wajib (Kaggle)

| Butir | Isi |
|---|---|
| Judul | Phishing URL - Websites Dataset (PhiUSIIL) |
| Pemilik | KagglePro (`kaggleprollc`) |
| Tautan | https://www.kaggle.com/datasets/kaggleprollc/phishing-url-websites-dataset-phiusiil |
| Versi | 1 ("Initial release"), diperbarui 2024-09-29 |
| Berkas | `PhiUSIIL_Phishing_URL_Dataset.csv`, 56.854.345 byte |
| Lisensi | CC BY-SA 4.0 |
| Rujukan yang dicantumkan Kaggle | Prasad & Chandra (2024), https://doi.org/10.1016/j.cose.2023.103545 |

Metadata di atas dibaca dari API publik Kaggle (`https://www.kaggle.com/api/v1/datasets/view/kaggleprollc/phishing-url-websites-dataset-phiusiil` dan `.../datasets/list/...`) pada 2026-11-26. Halaman HTML Kaggle perlu JavaScript sehingga lisensi belum dicocokkan langsung dengan tampilan halaman.

## Berkas yang dipakai dalam eksperimen

| Butir | Isi |
|---|---|
| Nama | `PhiUSIIL_Phishing_URL_Dataset.csv` |
| Ukuran | 56.854.345 byte (sama dengan ukuran berkas di Kaggle) |
| SHA-256 | `a236549cd369cd80bd478ff8e1779cbf44c58d5c3f79f7a51a1adbed7d06d1c6` |
| Tanggal unduh | belum pasti (berkas diterima dari anggota kelompok) |

Ukuran berkas sama persis dengan berkas Kaggle. Kesamaan hash belum diperiksa terhadap unduhan ulang dari Kaggle.

## Data asal

Kaggle menyalin dataset yang aslinya diterbitkan di Mendeley Data:

- Prasad, A. (2023). *PhiUSIIL phishing URL dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/shwpxscxy2.2, lisensi CC BY 4.0.
- Metadata DataCite (https://api.datacite.org/dois/10.17632/shwpxscxy2.2, dibaca 2026-11-26) mencantumkan satu *creator*, "Prasad, Arvind", dengan tanggal terbit 2023-11-15 dan lisensi CC BY 4.0. Shalini Chandra tercatat sebagai *contributor* (tipe "Other"), bukan *creator*. Paper pendampingnya ditulis Prasad dan Chandra (2024).
- Lisensi Kaggle (CC BY-SA 4.0) berbeda dari lisensi Mendeley (CC BY 4.0). Repositori ini tidak menyebarkan ulang data, hanya merujuk ke sumbernya.

## Label

Kolom `label`: 1 = legitimate, 0 = phishing (label asli). Pada eksperimen label dibalik sehingga phishing menjadi kelas positif (1).
