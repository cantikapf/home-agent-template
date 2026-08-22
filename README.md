# 🏡 Home Agent (WhatsApp Personal Assistant)

*Read this in [English](README-en.md)*

Selamat datang di repositori **Home Agent**, sebuah asisten rumah tangga pintar berbasis AI yang dapat diintegrasikan dengan WhatsApp Anda (via [Hermes Agent](https://github.com/cantikapf/hermes-agent)).

Proyek ini dibangun untuk mengotomatisasi berbagai urusan rumah tangga harian, mulai dari memantau isi kulkas, mencatat keuangan, hingga mengekstrak resep masakan langsung dari video TikTok menggunakan *Multimodal AI*.

## ✨ Fitur Utama

- 🛒 **Manajemen Daftar Belanja:** Menambah dan mencatat barang-barang yang perlu dibeli.
- 📦 **Inventaris Kulkas & Dapur:** Memantau stok bahan makanan secara *real-time*. AI akan memberikan peringatan jika bahan untuk resep tertentu tidak tersedia.
- 🍳 **Buku Resep Pintar:** Menyimpan daftar resep favorit Anda. AI bisa menyarankan resep berdasarkan stok bahan!
- 🎥 **Ekstraksi Resep TikTok:** Kemampuan super untuk "menonton" video resep TikTok menggunakan *Multimodal AI* (Gemini), mengekstrak bahan dan cara pembuatannya, lalu menyimpannya ke Buku Resep.
- 💸 **Pencatatan Pengeluaran:** Memantau pengeluaran harian/mingguan untuk kebutuhan rumah.

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
