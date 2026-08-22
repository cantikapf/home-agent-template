# 🏡 Home Agent (WhatsApp Personal Assistant)

*Read this in [English](README-en.md)*

Selamat datang di repositori **Home Agent**, sebuah asisten rumah tangga pintar berbasis AI yang dapat diintegrasikan dengan WhatsApp Anda (via [Hermes Agent](https://github.com/cantikapf/hermes-agent)).

Proyek ini dibangun untuk mengotomatisasi berbagai urusan rumah tangga harian, mulai dari memantau isi kulkas, mencatat keuangan, hingga mengekstrak resep masakan langsung dari video TikTok menggunakan *Multimodal AI*.

## ✨ Fitur Lengkap

🤖 **Sistem AI & Otomatisasi**
- **Multimodal AI:** Terintegrasi dengan Gemini Vision untuk menganalisis gambar dan video.
- **Daemon Cepat:** Menggunakan Unix Socket Server (`fast_daemon.py`) agar respon AI kilat tanpa memuat ulang Python/Firebase dari awal.
- **Auto-Shopping List:** Otomatis memasukkan barang ke daftar belanja jika mendeteksi stok dapur menipis (≤ 2).
- **Laporan Otomatis:** Mengirimkan rekap keuangan mingguan secara otomatis setiap hari Minggu pukul 19:00.

💸 **Manajemen Keuangan**
- Mencatat pengeluaran harian beserta deskripsi dan kategorinya.
- Menetapkan batas *budget* bulanan.
- Mengecek sisa uang dan persentase penggunaan *budget*.
- Melihat ringkasan pengeluaran bulan ini atau bulan-bulan sebelumnya.
- **Undo/Hapus:** Membatalkan atau menghapus pengeluaran jika salah ketik.

📦 **Inventaris Kulkas & Dapur**
- Memantau stok bahan makanan (tambah/kurang) secara *real-time*.
- Cek ketersediaan semua barang di dapur dalam satu perintah.
- **Combo Cerdas:** Saat Anda melapor "sudah beli [barang]", bot otomatis melakukan 3 hal: mencoretnya dari daftar belanja, menambah stok dapur, dan mencatatnya sebagai pengeluaran.

🛒 **Daftar Belanja**
- Menambah dan menghapus barang dari daftar belanja.
- Melihat daftar barang yang berstatus *pending* (belum dibeli).
- Membersihkan keranjang dari barang yang sudah dibeli.

🍳 **Buku Resep & TikTok**
- **Ekstrak Resep TikTok:** Kirimkan URL video masakan TikTok, dan AI akan "menontonnya" untuk menyalin resep dan cara membuatnya!
- Menyimpan resep favorit ke Buku Resep *database*.
- Melihat dan membaca ulang detail resep.
- Menghapus resep yang tidak disukai.
- **AI Chef:** Meminta AI membuatkan ide masakan kreatif berdasarkan stok bahan sisa di kulkas Anda.

⏰ **Pengingat (Reminders)**
- Membuat jadwal/alarm untuk urusan rumah (contoh: "ingatkan beli token listrik besok jam 10").
- Melihat daftar pengingat yang sedang aktif/berjalan.
- Membatalkan pengingat yang tidak lagi dibutuhkan.

## 🛠️ Prasyarat (Prerequisites)

Untuk menjalankan proyek ini di mesin Anda, Anda membutuhkan:

1. **Python 3.10+** terpasang di sistem.
2. **Hermes Agent** (atau framework WhatsApp bot serupa yang mendukung pemanggilan *command-line tools*).
3. **Google Gemini API Key** (Gratis di Google AI Studio).
4. **Firebase Firestore Database** (Gratis di Google Cloud/Firebase).
   - Buat proyek Firebase baru.
   - Buat Firestore Database.
   - Generate *Service Account Key* (Settings > Service Accounts > Generate new private key).

## 🚀 Instalasi & Setup

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/yourusername/home-agent-public.git
   cd home-agent-public
   ```

2. **Jalankan Setup Script:**
   Script ini akan menginstall dependensi dan mengganti path konfigurasi sesuai dengan direktori Anda.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Konfigurasi Kredensial:**
   - Ubah nama file Service Account Key dari Firebase menjadi `firebase-credentials.json` dan letakkan di dalam folder proyek ini.
   - Buka file `.env` dan masukkan `GEMINI_API_KEY` Anda.

4. **Integrasi dengan Hermes Agent:**
   - Folder `skills/` akan ter-generate (berisi instruksi Markdown untuk AI).
   - Pindahkan/copy isi folder `skills/` ke direktori skills milik bot Hermes Anda (misal: `~/.hermes/skills/home-agent/`).

5. **Jalankan Daemon:**
   Proyek ini menggunakan *socket daemon* yang sangat cepat (`fast_daemon.py`) agar model Python dan library Firebase tidak perlu dimuat ulang pada setiap pesan WhatsApp.
   ```bash
   # Aktifkan virtual environment
   source venv/bin/activate
   # Jalankan daemon
   python fast_daemon.py
   ```
   *(Sangat disarankan menjalankan daemon ini via `systemd` atau `pm2` agar berjalan di background).*


## 🪄 Instalasi Otomatis via AI (Cursor, Claude, Antigravity)
Malas melakukan setup manual? Jika Anda menggunakan *AI Coding Assistant* seperti **Cursor**, **Claude**, **Windsurf**, atau **Google Antigravity**, cukup berikan *prompt* (perintah) di bawah ini kepada AI Anda dan biarkan mereka yang mengerjakan semuanya:

```text
Tolong bantu saya menginstal proyek Home Agent dari repo https://github.com/cantikapf/home-agent-template.git.
1. Clone repositori tersebut ke direktori ini.
2. Buat virtual environment, aktifkan, dan install dependensi dari requirements.txt.
3. Jalankan chmod +x setup.sh dan jalankan skrip tersebut.
4. Beritahu saya cara mendapatkan Firebase Service Account Key dan Gemini API key, lalu tunggu saya menyediakannya.
5. Setelah saya memberikan kodenya, tolong buatkan file firebase-credentials.json dan .env.
6. Terakhir, jalankan `fast_daemon.py` di background dan pastikan tidak ada error.
```

## 🏗️ Arsitektur

- `home_agent.py`: Berisi seluruh logika bisnis (Firestore CRUD, Gemini Vision, dll).
- `fast_daemon.py`: Unix socket server yang me-*load* `home_agent.py` ke memory, sehingga pemrosesan jauh lebih cepat (menghindari overhead *cold start*).
- `fast_cli.py`: Klien CLI ringan yang dipanggil oleh Hermes Agent, meneruskan argumen terminal ke daemon via socket.
- `reminder_worker.py`: Worker background yang mengecek *reminders* (alarm) dari Firestore setiap 60 detik.
- `skills_template/`: Template instruksi untuk AI (Prompt RAG). Diubah menjadi folder `skills/` saat menjalankan `setup.sh`.

## 🤝 Berkontribusi (Contributing)

Silakan buat *Issue* atau kirimkan *Pull Request* jika Anda menemukan *bug* atau ingin menambahkan fitur baru! Kami sangat terbuka untuk kontribusi komunitas.

## 📄 Lisensi
[MIT License](LICENSE)
