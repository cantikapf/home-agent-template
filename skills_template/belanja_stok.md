---
name: belanja_stok
description: Mengelola daftar belanja, inventaris dapur/kulkas, dan struk belanja
---
# Instructions
Gunakan perintah ini untuk memodifikasi daftar belanja atau stok:
`{{PYTHON_BIN}} {{FAST_CLI_PATH}}`

## 🛒 Daftar Belanja

### Tambah ke Daftar Belanja
Jika pengguna memberikan tautan/URL (seperti link Shopee, Tokopedia, dll), **jadikan seluruh link tersebut sebagai `--item`**. Sistem akan secara otomatis mengekstrak nama barangnya dari link tersebut!
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action shopping --item "<nama_barang_ATAU_link_ecommerce>" --qty <angka> --unit "<satuan>" --category "<kategori>"
# Contoh:
# {{PYTHON_BIN}} {{FAST_CLI_PATH}} --action shopping --item "https://shopee.co.id/xxx" --qty 1 --category "Lain-lain"
```

### Lihat Daftar Belanja
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_shopping_list
```

### Hapus dari Daftar Belanja
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action remove_shopping --item "<nama_barang>"
```

### Bersihkan Semua yang Sudah Dibeli
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action clear_bought
```

### Tandai Sudah Dibeli (Tanpa Catat Pengeluaran)
Jika pengguna hanya ingin menandai item sebagai "sudah dibeli" tanpa mencatat harga/stok:
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action mark_bought --item "<nama_barang>"
```

### ⭐ SUDAH BELI COMBO (SANGAT PENTING - WAJIB TERMINAL)
Saat pengguna bilang "sudah beli [barang]" atau mengunggah **Foto Struk Belanja**, Anda **DILARANG KERAS** hanya menjawab dengan teks! Anda **WAJIB** mengeksekusi perintah CLI `bought` ini di terminal.
Ini akan otomatis menghapus dari daftar belanja + tambah stok + catat pengeluaran!
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action bought --item "<nama_barang>" --qty <angka> --amount <harga> --category "<kategori>" --unit "<satuan>"
```

## 📦 Stok/Inventori Kulkas & Dapur

### Update Stok Barang Manual
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action inventory --item "<nama_barang>" --qty <angka> --inv_action <add|use> --unit "<satuan>"
```
(--inv_action add untuk tambah, use untuk kurangi)

### Lihat Semua Stok
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_inventory
```

## 📸 Foto Struk Belanja (Vision)

### ATURAN UTAMA
- Kamu WAJIB membaca foto struk dengan teliti menggunakan kemampuan vision-mu.
- JANGAN PERNAH mengarang atau menebak harga. Jika tidak terbaca, TANYAKAN ke pengguna.
- Jika foto terlalu buram/gelap, minta pengguna kirim ulang foto yang lebih jelas.

### Langkah-langkah Wajib

**Langkah 1: Baca & Ekstrak**
Baca semua item dari foto struk. Ekstrak informasi berikut untuk setiap item:
- Nama barang
- Jumlah/kuantitas (jika tertera, default: 1)
- Harga satuan atau harga total item tersebut
- Satuan (kg, pcs, liter, pack, dll — jika tertera)

**Langkah 2: Deteksi Kategori Otomatis**
Tentukan kategori pengeluaran berdasarkan jenis barang:
- Bahan makanan mentah (sayur, daging, ikan, telur, bumbu) → `Groceries`
- Makanan jadi/snack/minuman kemasan → `Makanan & Minuman`
- Produk kebersihan (sabun, deterjen, pel) → `Household`
- Produk perawatan diri (shampo, skincare, pasta gigi) → `Personal Care`
- Lain-lain → `Lain-lain`

**Langkah 3: Konfirmasi ke Pengguna**
Tampilkan hasil bacaan dalam format tabel yang rapi, contoh:

```
📸 Saya baca dari struk kamu:

| No | Barang         | Qty | Satuan | Harga      | Kategori    |
|----|----------------|-----|--------|------------|-------------|
| 1  | Beras 5kg      | 1   | karung | Rp 75.000  | Groceries   |
| 2  | Telur Ayam     | 1   | kg     | Rp 28.000  | Groceries   |
| 3  | Sabun Cuci     | 2   | pcs    | Rp 15.000  | Household   |
|    |                |     | TOTAL  | Rp 118.000 |             |

Ada yang perlu dikoreksi? Kalau sudah benar, bilang "oke" atau "lanjut" ya!
```

**Langkah 4: Eksekusi Setelah Konfirmasi**
Setelah pengguna mengonfirmasi (bilang "oke", "lanjut", "benar", "yes", dll), jalankan perintah `bought` untuk SETIAP item:
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action bought --item "<nama_barang>" --qty <angka> --amount <harga> --category "<kategori>" --unit "<satuan>"
```

⚠️ PENTING: Jalankan satu perintah `bought` per item, JANGAN digabung!

**Langkah 5: Rangkuman**
Setelah semua item diproses, berikan rangkuman singkat:
```
✅ Semua [N] item dari struk berhasil dicatat!
💰 Total pengeluaran: Rp XXX
📦 Stok yang diperbarui: [daftar item]
```

### Penanganan Masalah
- **Harga tidak terbaca**: Tulis "❓" di kolom harga dan tanyakan ke pengguna
- **Nama barang terpotong/singkatan**: Tebak nama lengkapnya dan tandai dengan "(❓)" agar pengguna bisa koreksi
- **Diskon/potongan harga**: Gunakan harga SETELAH diskon (harga yang benar-benar dibayar)
- **Struk panjang terpotong**: Beritahu pengguna bahwa struk terpotong dan minta foto bagian sisanya
- **Ada item yang BUKAN belanja rumah tangga** (misal: pulsa, parkir): Tetap catat tapi gunakan kategori yang sesuai