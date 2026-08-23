# 🏡 Home Agent (WhatsApp Personal Assistant)

Selamat datang di repositori **Home Agent**, sebuah asisten rumah tangga pintar berbasis AI (Artificial Intelligence) yang terintegrasi langsung dengan WhatsApp Anda.

Proyek ini dibangun untuk mengotomatisasi berbagai urusan rumah tangga harian, mulai dari memantau isi kulkas hingga mengekstrak resep masakan langsung dari video TikTok!

## ✨ Fitur Utama

- 🛒 **Manajemen Daftar Belanja:** Menambah, menghapus, dan mencatat daftar belanja. Dilengkapi ekstraksi otomatis nama produk dari URL e-commerce (Shopee & Tokopedia) mem-bypass skeleton SPA.
- 📸 **Pembacaan Struk Belanja (Vision AI):** AI bisa "melihat" dan membaca foto struk belanja, mengekstrak harga, dan mengkategorikan pengeluaran secara otomatis.
- 📦 **Inventaris Kulkas & Dapur:** Memantau stok bahan makanan secara *real-time* dan otomatis memasukkan barang ke daftar belanja jika stok menipis.
- 🍳 **Buku Resep Pintar & Ekstraktor Video:** Ekstrak bahan dan cara pembuatan resep langsung dari video TikTok/YouTube menggunakan *Multimodal AI* (anti-bot protection bypass).
- 💸 **Pencatatan Keuangan & Budgeting:** Pantau budget bulanan, catat pengeluaran harian, dan lihat persentase pemakaian saldo (mendukung spesifik bulan).
- ⏰ **Pengingat & Laporan Mingguan:** Atur pengingat/alarm (reminder), serta laporan mingguan otomatis (pengeluaran, sisa budget, stok habis) setiap hari Minggu jam 19:00.
- 📝 **TL;DR & Session Recap:** Rangkum teks artikel/chat yang panjang, atau minta AI memberikan rangkuman seluruh pekerjaan yang sudah diselesaikan pada sesi saat ini.

## 🛠️ Teknologi yang Digunakan

- **AI Engine:** Google Gemini (Gemini 2.5 Flash & Flash-Lite) melalui kerangka kerja **Hermes Agent**.
- **WhatsApp Bridge:** Node.js (menggunakan *library* Baileys).
- **Database:** Firebase Firestore (Google Cloud Platform).
- **Server / Hosting:** Oracle Cloud Infrastructure (OCI) - Ubuntu VPS.
- **CI/CD:** GitHub Actions.

## 🚀 CI/CD Pipeline (Cara Deploy Kode)

Repositori ini telah dilengkapi dengan sistem *Continuous Integration / Continuous Deployment* (CI/CD) yang sepenuhnya otomatis.

Setiap kali ada perubahan pada file kode (misalnya home_agent.py atau AGENTS.md), Anda **TIDAK PERLU** lagi masuk (SSH) ke dalam VPS atau melakukan *upload* manual (SCP/FTP). 

**Cukup lakukan langkah berikut di lokal:**
```bash
git add .
git commit -m "Deskripsi perubahan kode"
git push origin main
```
Dalam hitungan detik, GitHub Actions akan secara otomatis:
1. Masuk secara aman ke mesin Oracle VPS Anda.
2. Memperbarui file-file yang berubah.
3. Melakukan *restart* pada layanan hermes-gateway.service.
4. Bot WhatsApp Anda akan langsung menggunakan versi kode terbaru!

## 🔐 Keamanan Data (Security)

Repositori ini berstatus **Private**. Beberapa file sangat rahasia dan telah diblokir secara permanen oleh .gitignore agar tidak bocor, yaitu:
- File kunci SSH (*.key)
- Kredensial Firebase Cloud (*.json)
- Konfigurasi environment (.env)

Harap pastikan file-file di atas tetap berada di lokal/mesin VPS dan jangan pernah dihapus dari .gitignore.
