# 🏡 Home Agent (WhatsApp Personal Assistant)

*[Read in English](README-en.md)*

Home Agent adalah bot asisten pribadi berbasis AI yang saya bikin untuk ngurusin hal-hal remeh tapi penting di rumah tangga, langsung dari chat WhatsApp.

Capek ngecek kulkas kosong? Males ngetik ulang resep dari video TikTok? Atau pengen nyatet pengeluaran harian cuma modal foto struk belanja? Nah, bot ini yang bakal ngerjain itu semua.

## ✨ Fitur Utama

- 🛒 **Daftar Belanja Pintar:** Gak cuma nyatet belanjaan biasa, kalau kamu kirim link dari Shopee atau Tokopedia, bot bisa langsung nge-ekstrak nama barangnya otomatis.
- 🧾 **Tinggal Foto Struk (Vision AI):** Malas nyatet pengeluaran satu-satu? Foto aja struk belanjanya. AI bakal baca harganya, nge-total, dan masukin ke kategori pengeluaran yang pas.
- ❄️ **Manajemen Kulkas & Dapur:** Cek sisa stok bahan makanan.
- 🍳 **Buku Resep & Video Extractor:** Punya video resep dari TikTok atau YouTube? Kirim aja link-nya. Multimodal AI bakal nonton videonya dan nyatet bahan serta cara masaknya ke database resep kamu.
- 💰 **Manajemen Keuangan Terpadu:** Pantau pengeluaran harian/mingguan, catat tagihan bulanan (Bills), hingga pencatatan aset investasi/tabungan liquid (Assets). Tiap nyatat pengeluaran, bot ngasih tahu sisa budget bulanan.
- ⏰ **Reminder & Weekly Report:** Pasang alarm satu kali atau berulang (harian/mingguan). Plus, tiap minggu bot otomatis kirim laporan keuangan.
- 🤖 **Mistral AI Engine:** Ditenagai oleh Mistral (super cepat & irit) untuk logika utama dan ekstraksi data cerdas.

## 📱 TikTok Bulk Importer (Tutorial)

Buat kamu yang punya ratusan video resep favorit di TikTok dan pengen memindahkannya ke database Home Agent secara otomatis, kamu bisa pakai script *Bulk Importer*:

1. **Request Data TikTok:** Buka aplikasi TikTok > *Settings and privacy* > *Account* > *Download your data*. Pilih format **JSON**!
2. **Scan Resep:** Taruh file `user_data_tiktok.json` di dalam folder proyek ini (`tiktok_data` jika perlu), lalu jalankan:
   ```bash
   python scripts/scan_tiktok_recipes.py
   ```
   Skrip ini akan menyeleksi mana video yang kemungkinan besar adalah resep masakan berdasarkan judulnya (memakan waktu ~1 menit).
3. **Ekstrak & Impor:** Setelah beres, jalankan:
   ```bash
   python scripts/import_tiktok_recipes.py
   ```
   AI bakal "menonton" dan membaca satu per satu ratusan video tersebut, lalu menyimpannya ke Buku Resep kamu secara otomatis. Skrip ini punya fitur *Auto-Resume* jadi aman kalau terputus!
## 📊 Gimana Cara Kerjanya? (Arsitektur)

Biar gak lemot dan *cold start*, saya bikin arsitekturnya pakai *daemon socket*. Jadi, Firebase dan AI model-nya tetap *standby* di memori server. Kalau ada chat masuk, eksekusinya kilat!

```mermaid
sequenceDiagram
    participant User as 📱 WhatsApp (User)
    participant Hermes as 🤖 Hermes Agent (Node.js)
    participant CLI as ⌨️ Fast CLI (Python)
    participant Daemon as ⚙️ Fast Daemon (Socket)
    participant Mistral as 🧠 Mistral AI
    participant Firebase as 🗄️ Firestore (Database)

    User->>Hermes: Chat / Foto / Video
    Hermes->>Mistral: Pahami maksud chat & ekstrak instruksi
    Mistral-->>Hermes: Tentukan Tool (Misal: "Catat Belanja Susu")
    Hermes->>CLI: Eksekusi Tool (fast_cli.py --action shopping --item Susu)
    CLI->>Daemon: Kirim via Unix Socket (Proses Instan)
    Daemon->>Firebase: Simpan "Susu" ke database
    Firebase-->>Daemon: Sukses
    Daemon-->>CLI: Return hasil
    CLI-->>Hermes: Output eksekusi
    Hermes->>User: Balas WA ("Susu berhasil dicatat! ✅")
```

### 🧠 Arsitektur Model & AI Routing (Failover System)
Karena *system prompt* bot ini sangat besar, bot menggunakan strategi multi-model untuk efisiensi biaya dan reliabilitas tinggi (anti *down*):

```mermaid
graph TD
    User([📱 WhatsApp User]) -->|Kirim Pesan/Foto| Hermes(🤖 Hermes Agent)
    
    subgraph AI Routing Strategy
        Hermes -->|Instruksi CLI / Chat| Router(🔄 9router Load Balancer)
        Hermes -->|Gambar & Struk Belanja| Vision(👁️ Auxiliary Vision)
        
        Router -->|Prioritas Utama| Vikey(🟢 Vikey AI<br>deepseek-v4-flash)
        Router -.->|Fallback / Limit| MistralPool(🟠 Mistral Pool<br>mistral-large-latest)
        
        MistralPool -.-> M1(Mistral API Key 1)
        MistralPool -.-> M2(Mistral API Key 2)
        MistralPool -.-> M3(Mistral API Key 3)
        MistralPool -.-> M4(Mistral API Key 4)
        
        Vision --> Gemini(🔵 Gemini 3.5 Flash)
    end
    
    classDef primary fill:#d4edda,stroke:#28a745,stroke-width:2px,color:black;
    classDef fallback fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:black;
    classDef vision fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:black;
    classDef router fill:#e2e3e5,stroke:#383d41,stroke-width:2px,color:black;
    
    class Vikey primary;
    class MistralPool,M1,M2,M3,M4 fallback;
    class Vision,Gemini vision;
    class Router router;
```
1. **DeepSeek (Vikey AI)**: Otak utama (termurah & sangat stabil untuk mengeksekusi instruksi Python).
2. **Mistral Pool (via 9router)**: Jika saldo Vikey AI habis atau limit, *Smart Model Routing* akan beralih ke 9router yang membagi beban ke 4 API Key Mistral secara otomatis.
3. **Gemini 3.5 Flash**: Ditugaskan secara independen dan *headless* khusus hanya saat pengguna mengirimkan foto.

## 🛠️ Tech Stack

- **AI Engine:** Mistral API di-handle oleh framework **Hermes Agent**.
- **WhatsApp Bridge:** Node.js (via Baileys).
- **Database:** Firebase Firestore (GCP).
- **Hosting:** Oracle Cloud VPS (Ubuntu).
- **CI/CD:** GitHub Actions.

## 🚀 CI/CD Pipeline (Auto-Deploy)

Setiap ada perubahan kode yang di-push ke branch `main`, GitHub Actions bakal otomatis nge-trigger *runner* masuk ke VPS (via SSH), narik kode terbaru, dan nge-restart service bot di server. Jadi gak perlu repot *remote* server tiap kali ada *update* fitur.

## 🔒 Security & Setup Kredensial

Tenang, data rahasia kayak `.env`, file kredensial `.json` dari Firebase, dan *private key* SSH (`.key`) udah aman di-block sama `.gitignore`.

Kalau kamu mau jalanin atau me- *fork* bot ini di komputer sendiri:
1. Copy `.env.example` jadi `.env` lalu masukin API Key Mistral kamu.
2. Letakkan file *service account* Firebase kamu (`firebase-credentials.json`) di folder *root*.
3. Setup dan jalankan *daemon* Python-nya!
