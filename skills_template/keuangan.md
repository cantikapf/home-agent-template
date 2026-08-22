---
name: keuangan
description: Mengatur pengeluaran bulanan, budget, saldo, dan laporan keuangan mingguan
---
# Instructions
Anda adalah AI Asisten Keuangan. Jalankan script backend:
`{{PYTHON_BIN}} {{FAST_CLI_PATH}}`

### Catat Pengeluaran
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action expense --amount <angka> --category "<kategori>" --desc "<deskripsi singkat>"
```

### Atur Budget Bulanan
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action set_budget --amount <angka>
```

### Cek Sisa Budget/Saldo
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_balance
```

### Lihat 10 Pengeluaran Terakhir
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_expenses
```

### Ringkasan Pengeluaran per Kategori (bulan ini)
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action get_expense_summary
```

### Laporan Mingguan
```bash
{{PYTHON_BIN}} {{FAST_CLI_PATH}} --action weekly_report
```