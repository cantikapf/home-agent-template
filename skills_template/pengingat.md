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