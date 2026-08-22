---
name: resep_masakan
description: Mencari ide resep, mengekstrak resep dari link TikTok, membaca dan menghapus detail buku resep
---
# Instructions
Anda bertugas membantu mencari ide masakan dan mengekstrak resep.
`{{PYTHON_BIN}} {{FAST_CLI_PATH}}`

## 🍳 Resep Manual & Ide Masakan

### Saran Memasak
Jika pengguna bertanya "Masak apa hari ini?":
1. Panggil skill `get_inventory` untuk melihat stok bahan.
2. Panggil action `get_recipes` (di bawah) untuk melihat Buku Resep.
3. Prioritaskan resep di Buku Resep yang cocok dengan stok. Jika bahan kurang, sarankan substitusi atau tawarkan memasukkannya ke daftar belanja.

### Buatkan Resep Baru (Kreasi AI)
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action recipe --ingredients "<bahan-bahan>"
```

## 📱 TikTok & Ekstraksi Resep

### Ekstrak Resep dari Tautan (URL TikTok / YouTube)
**ATURAN KERAS**: JANGAN PERNAH membuat script Python buatan sendiri (seperti `python3 -c` atau `requests`) untuk membaca tautan. Anda WAJIB menggunakan ini:
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action extract_video --url "<link_yang_diberikan>"
```
Setelah mendapat hasil, buat draf resep dan tanyakan "Apakah boleh disimpan?". JANGAN simpan sebelum disetujui.

### Simpan Resep ke Buku Resep
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action save_recipe --name "<nama masakan>" --ingredients "<bahan-bahan>" --steps "<cara membuat>" --url "<url sumber>"
```

### Lihat Semua Buku Resep
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_recipes
```

### Baca Detail Resep
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action read_recipe --name "<nama resep>"
```

### Hapus Resep dari Buku
Jika pengguna meminta menghapus resep yang salah atau tidak disukai:
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action delete_recipe --name "<nama resep>"
```
