# TikTok Bulk Recipe Importer

Tools ini membantu Anda mengekstrak ratusan video resep yang pernah Anda "Favorite"-kan di TikTok, dan memasukkannya secara otomatis ke dalam **Recipe Book Firestore (Home Agent)** menggunakan Gemini AI.

## Persyaratan
- Python 3.8+
- Koneksi internet (untuk menembak API TikTok dan Gemini)
- Kredensial Firebase (`firebase-credentials.json`) sudah dikonfigurasi di *root* proyek.

## Langkah 1: Dapatkan Data Ekspor TikTok Anda
1. Buka aplikasi TikTok di HP Anda.
2. Pergi ke **Settings and privacy** -> **Account** -> **Download your data**.
3. Pilih format **JSON** (Sangat Penting!).
4. Tunggu beberapa hari hingga TikTok menyiapkan file Anda.
5. Unduh file ZIP tersebut, ekstrak, dan temukan file bernama `user_data_tiktok.json`.
6. Pindahkan file `user_data_tiktok.json` ke folder `tools/tiktok_bulk_importer/` ini.

## Langkah 2: Pindai dan Filter Resep
Jalankan skrip *scanner* untuk membaca seluruh video favorit Anda dan menyaring video yang kemungkinan besar adalah resep (berdasarkan judulnya).

```bash
pip install aiohttp
python scan_tiktok_recipes.py
```
Skrip ini akan memindai ribuan URL dengan cepat (kurang dari 2 menit) dan menghasilkan file baru bernama `tiktok_recipes_found.json`.

*Catatan: Anda bebas mengedit file `tiktok_recipes_found.json` secara manual jika ada resep yang ingin Anda hapus sebelum diimpor.*

## Langkah 3: Ekstrak dan Impor ke Database
Jalankan skrip *importer* untuk memerintahkan Gemini AI menonton video tersebut dan menyimpannya ke Firebase Anda.

```bash
python import_tiktok_recipes.py
```

Jika Anda menggunakan *Virtual Environment* untuk menjalankan Home Agent, pastikan Anda menunjuk *python executable* yang benar:
```bash
# Di Windows
python import_tiktok_recipes.py --python-cmd "..\..\venv\Scripts\python.exe"

# Di Linux/Mac
python import_tiktok_recipes.py --python-cmd "../../venv/bin/python"
```

Skrip ini dilengkapi fitur **Auto-Resume**. Jika terputus di tengah jalan, jalankan ulang perintah yang sama, dan skrip akan melanjutkan dari video terakhir yang diproses!
