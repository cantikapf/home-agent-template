---
name: belanja_stok
description: Mengelola daftar belanja, inventaris dapur/kulkas, dan struk belanja
---
# Instructions
Gunakan perintah ini untuk memodifikasi daftar belanja atau stok:
`{{PYTHON_BIN}} {{FAST_CLI_PATH}}`

## 🛒 Daftar Belanja

### Tambah ke Daftar Belanja
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action shopping --item "<nama_barang>" --qty <angka> --unit "<satuan>"
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

### ⭐ SUDAH BELI COMBO (SANGAT PENTING)
Saat pengguna bilang "sudah beli [barang]" atau mengunggah **Foto Struk Belanja**, Anda WAJIB menggunakan action ini.
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
Jika pengguna mengirim **foto struk/bon belanja**:
1. Baca semua item dan harganya dari foto.
2. Konfirmasi ke pengguna.
3. Gunakan action `bought` untuk setiap item.