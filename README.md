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
        
        Router -->|Prioritas Utama| MistralPool(🟠 Mistral Pool<br>mistral-large-latest)
        Router -.->|Fallback / Limit| Vikey(🟢 Vikey AI<br>llama-3.1-70b-instruct)
        
        MistralPool -.-> M1(Mistral API Key 1)
        MistralPool -.-> M2(Mistral API Key 2)
        MistralPool -.-> M3(Mistral API Key 3)
        MistralPool -.-> M4(Mistral API Key 4)
        
        Router -->|Input Gambar/Struk| Gemini(🔵 Gemini 1.5 Flash Vision Adapter)
    end
    
    subgraph Development & CLI Tools
        Router -.- Groq(Groq API)
        Router -.- Nvidia(NVIDIA NIM)
        Router -.- OpenRouter(OpenRouter)
        Router -.- GitHub(GitHub Models)
    end
    
    classDef primary fill:#d4edda,stroke:#28a745,stroke-width:2px,color:black;
    classDef fallback fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:black;
    classDef vision fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:black;
    classDef router fill:#e2e3e5,stroke:#383d41,stroke-width:2px,color:black;
    classDef aux fill:#f8f9fa,stroke:#ced4da,stroke-width:2px,color:black;
    
    class MistralPool,M1,M2,M3,M4 primary;
    class Vikey fallback;
    class Gemini vision;
    class Router router;
    class Groq,Nvidia,OpenRouter,GitHub aux;
```
1. **9Router API Gateway**: Seluruh *API Key* tidak lagi disimpan di file `.env` Hermes Agent, melainkan dikelola terpusat oleh 9Router (`http://localhost:20128/v1`).
2. **Mistral Pool (Prioritas Utama)**: Menggunakan 4 buah API Key dari Mistral yang dipasangkan ke dalam fitur *Combo* 9Router untuk menangani *heavy workload* tanpa terbentur *rate limit* gratisan (menghemat biaya 100%).
3. **Vikey AI (Fallback)**: Diposisikan di urutan terakhir dalam Combo. Hanya akan memotong saldo (berbayar) apabila ke-4 kunci Mistral mati secara bersamaan. Dilengkapi dengan *Semantic Caching* (Token Saver) untuk menekan *cost* lebih jauh.
4. **Gemini 1.5 Flash (Vision Adapter)**: Di-setting khusus pada level *Router* (bukan di Hermes). Ketika pengguna mengirim gambar, router akan mendeteksi kebutuhan `image_url` dan secara otomatis mengalihkannya ke kunci Gemini.
5. **Auxiliary Keys**: Kunci tambahan seperti Groq, NVIDIA, HuggingFace, Cloudflare, dan GitHub diintegrasikan di 9Router untuk dipakai saat eksperimen atau lewat *CLI Tools* IDE tanpa mengganggu stabilitas bot WhatsApp.

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
