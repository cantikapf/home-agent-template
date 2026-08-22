---
name: pengingat
description: Mengelola alarm atau pengingat jadwal untuk urusan rumah tangga
---
# Instructions

### Tambah Pengingat
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action add_reminder --task "<isi pengingat>" --time "<waktu dalam format YYYY-MM-DD HH:MM>"
```
Contoh: `--task "Beli gas LPG" --time "2026-08-23 10:00"`

### Lihat Daftar Pengingat Aktif
Jika pengguna bertanya "ada pengingat apa saja?":
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_reminders
```

### Batalkan (Hapus) Pengingat
Jika pengguna meminta membatalkan pengingat yang sudah dibuat:
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action delete_reminder --task "<nama atau sebagian nama task>"
```
