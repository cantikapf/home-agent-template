# 🏡 Home Agent — Intelligent Household OS & Personal Assistant

<p align="center">
  <img src="docs/assets/home-agent-banner.svg" alt="Home Agent Banner" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/cantikapf/home-agent-template/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Next.js-16%20App%20Router-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js 16" />
  <img src="https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black" alt="Firebase Firestore" />
  <img src="https://img.shields.io/badge/AI%20Gateway-9Router-7C3AED?style=flat-square&logo=openai&logoColor=white" alt="9Router" />
  <img src="https://img.shields.io/badge/AWS-Graviton%20ARM64-FF9900?style=flat-square&logo=amazonec2&logoColor=white" alt="AWS EC2" />
</p>

<p align="center">
  <b>Asisten rumah tangga otonom berbasis Multimodal AI via WhatsApp dan Web Dashboard Next.js real-time.</b><br />
  Pencatatan struk belanja instan (Vision AI), arus kas riil tanpa budget statis (Aturan Wants 50/30/20), manajemen stok kulkas, dan ekstraksi resep TikTok/YouTube otomatis.
</p>

<p align="center">
  <a href="README.md"><b>Bahasa Indonesia</b></a> • <a href="README-en.md">Read in English</a>
</p>

---

## 📸 Antarmuka & Preview Sistem

| **Ringkasan Keuangan & Arus Kas (`/finance`)** | **System Overview & Health (`/`)** |
|:---:|:---:|
| ![Finance Dashboard Preview](docs/assets/dashboard-preview.svg) | ![System Overview Preview](docs/assets/system-overview.svg) |

<p align="center">
  <b>Interaksi Asisten WhatsApp (Vision OCR Struk &amp; Resep Masakan):</b><br />
  <img src="docs/assets/whatsapp-chat.svg" alt="WhatsApp Chat Preview" width="560px" />
</p>

---

## ✨ Fitur Utama

- 🧾 **Tinggal Foto Struk (Vision AI):** Malas mengetik pengeluaran satu per satu? Cukup kirim foto struk belanjaan di WhatsApp. Google Gemini 2.5 Flash membaca item belanja, nominal, menjumlahkan total, dan mengklasifikasikan kategori secara instan.
- 💰 **Zero-Budgeting & Pemantauan Wants 50/30/20:** Sistem tidak menggunakan batas budget bulanan statis yang tidak realistis. Keuangan berpusat pada **Saldo Kas Liquid** riil. Pengeluaran gaya hidup (*Wants*) dipantau ketat di bawah rasio 30% pengeluaran bulanan. Jika boros, asisten akan menegur secara tegas.
- ❄️ **Manajemen Kulkas & Stok Dapur:** Pantau bahan makanan di kulkas dengan satuan dinamis (butir, kg, liter), status stok rendah, dan pengurangan otomatis saat memasak.
- 🛒 **Daftar Belanja Terpadu:** Catat rencana belanjaan. Saat barang dibeli (`ha --action bought`), sistem otomatis mencatat pengeluaran, mengurangi saldo kas liquid, dan memindahkan barang ke stok kulkas. Mendukung ekstraksi link produk Shopee/Tokopedia.
- 🍳 **Ekstraktor Resep Video (TikTok & YouTube):** Kirim link video masakan, AI multimodal akan menonton video tersebut dan mengekstrak bahan serta panduan langkah memasak ke database resep.
- ⏰ **Pengingat Cerdas & Laporan Mingguan:** Pasang alarm satu kali atau berulang (*daily/weekly/monthly*). Setiap Minggu malam, bot mengirimkan ringkasan arus kas mingguan langsung ke WhatsApp.
- ⚡ **Zero Cold-Start Python Daemon:** Arsitektur *in-memory Unix domain socket* menjaga koneksi Firebase dan modul Python tetap hangat di RAM server untuk latensi eksekusi sub-detik.
- 🔀 **Multi-Tier AI Brain (9Router Gateway):** Routing cerdas 3 lapis (**DeepSeek V4 Flash** primary ➔ **Mistral Medium** fallback 1 ➔ **Gemini 2.5 Flash** fallback 2) untuk jaminan uptime 99.9% dengan biaya operasional sangat hemat.

---

## 📊 Visualisasi Alur Kerja & Arsitektur

### 1. Siklus Hidup Permintaan (Request Lifecycle)
Alur interaksi dari pesan WhatsApp pengguna hingga mutasi data di Firestore dan respon kembali ke pengguna:

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 WhatsApp (User)
    participant GW as 🤖 Hermes Gateway (Port 3000)
    participant Router as 🔀 9Router Proxy (Port 20128)
    participant LLM as 🧠 AI Brain (DeepSeek / Gemini)
    participant CLI as ⌨️ Fast CLI (ha)
    participant Daemon as ⚙️ Fast Daemon (Unix Socket)
    participant DB as 🗄️ Firestore (Database)

    User->>GW: Kirim Chat / Foto Struk / Link Resep
    alt Foto Struk Belanja
        GW->>Router: Forward Vision Payload (Gemini 2.5 Flash)
        Router-->>GW: Structured OCR Data (Items, Total, Category)
    else Pesan Teks
        GW->>Router: Chat Completion Request
        Router->>LLM: 3-Tier Failover (DeepSeek ➔ Mistral ➔ Gemini)
        LLM-->>Router: Tool Calling Decision (CLI ha)
        Router-->>GW: Forward Tool Call
    end
    GW->>CLI: Eksekusi Tool (ha --action ...)
    CLI->>Daemon: Kirim IPC via Unix Domain Socket (/tmp/home_agent.sock)
    Daemon->>DB: Mutasi Dokumen / Auto-deduct Kas Liquid
    DB-->>Daemon: Konfirmasi Snapshot
    Daemon-->>CLI: JSON Response Status
    CLI-->>GW: Formatted Output
    GW->>User: Balas WhatsApp (Format Bullet Points Emoji)
```

---

### 2. Topologi Infrastruktur Server & Port
Arsitektur proses background di server AWS EC2 Graviton dan tunneling Cloudflare Zero Trust:

```mermaid
flowchart TD
    subgraph Clients ["Klien Pengguna"]
        WA["📱 WhatsApp Client (Mobile / Web)"]
        Browser["💻 Web Browser (Modern UI)"]
    end

    subgraph Tunnel ["Cloudflare Ingress Layer"]
        CFD["☁️ Cloudflare Zero Trust Tunnel (cloudflared)"]
    end

    subgraph VPS ["AWS EC2 Graviton ARM64 (Ubuntu 24.04 LTS)"]
        subgraph SystemdUnits ["Systemd User Services"]
            HGW["🤖 hermes-gateway.service<br><i>(Port 3000 - Baileys WA Bridge)</i>"]
            WebDash["🌐 hermes-dashboard.service<br><i>(Port 8501 - Next.js 16 Standalone)</i>"]
            NineR["🔀 9router.service<br><i>(Port 20128 - AI Load Balancer)</i>"]
            FDaemon["⚙️ home-agent-daemon.service<br><i>(Unix Socket: /tmp/home_agent.sock)</i>"]
            RemWorker["⏰ reminder-worker.service<br><i>(Background Scheduler)</i>"]
        end
    end

    subgraph CloudServices ["Layanan Cloud & AI Eksternal"]
        DeepSeek["⚡ Vikey / DeepSeek V4 Flash"]
        Mistral["🟠 Mistral AI API Pool"]
        Gemini["🔵 Google Gemini 2.5 Flash Vision"]
        Firestore[("🔥 Google Cloud Firestore Database")]
    end

    WA <-->|End-to-End Encrypted WS| HGW
    Browser <-->|HTTPS: custom domain| CFD
    CFD <-->|Port 8501| WebDash
    CFD <-->|Port 20128| NineR

    HGW -->|Proxy /v1/chat| NineR
    NineR -->|Primary| DeepSeek
    NineR -.->|Fallback 1| Mistral
    NineR -.->|Fallback 2| Gemini

    HGW -->|Panggil CLI `ha`| FDaemon
    RemWorker -->|Polling & Cron| Firestore
    RemWorker -->|Kirim Pesan WA| HGW
    FDaemon -->|Query & Mutasi| Firestore
    WebDash -->|Server-side firebase-admin| Firestore

    classDef client fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef server fill:#f8fafc,stroke:#475569,stroke-width:2px,color:#0f172a;
    classDef cloud fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#0f172a;
    class WA,Browser client;
    class HGW,WebDash,NineR,FDaemon,RemWorker,CFD server;
    class DeepSeek,Mistral,Gemini,Firestore cloud;
```

---

### 3. Arsitektur AI Fallback & Token Saver (9Router)
Sistem proteksi multi-provider untuk mencegah downtime atau rate limit:

```mermaid
graph TD
    Request([📥 Permintaan Chat / Tool Call]) --> NineRouter[🔀 9Router Proxy Gateway]
    
    subgraph ComboBrain ["hermes-fallback (Model Teks & CLI)"]
        NineRouter -->|Tingkat 1 - Biaya Super Hemat| DeepSeek["🟢 DeepSeek V4 Flash (Primary)"]
        DeepSeek -.->|Jika HTTP 429 / 5xx| Mistral["🟠 Mistral Medium (Fallback 1)"]
        Mistral -.->|Jika Limit Habis| GeminiChat["🔵 Gemini 2.5 Flash (Fallback 2)"]
    end

    subgraph VisionPipeline ["Adapter Gambar & Struk"]
        NineRouter -->|Deteksi gambar base64 / URL| GeminiVision["🟣 Gemini 2.5 Flash Vision Direct"]
    end

    subgraph OptimizationLayer ["Token Saver & Cache"]
        DeepSeek --- Headroom["⚡ Headroom AI Proxy"]
        DeepSeek --- SemanticCache["💾 Semantic Prompt Caching"]
    end

    classDef primary fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef fallback fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    classDef vision fill:#f3e8ff,stroke:#9333ea,stroke-width:2px,color:#581c87;
    class DeepSeek,Headroom primary;
    class Mistral,GeminiChat fallback;
    class GeminiVision vision;
```

---

### 4. Skema Relasi Data (Firestore Collections)
Model data NoSQL yang menghubungkan mutasi belanja, kulkas, kas, dan resep:

```mermaid
erDiagram
    ASSETS ||--o{ EXPENSES : "auto-deduct saat transaksi"
    SHOPPING_ITEMS }o--|| INVENTORY_ITEMS : "pindah stok saat dibeli"
    RECIPES ||--o{ INVENTORY_ITEMS : "rekomendasi menu berbasis stok"

    ASSETS {
        string id PK "contoh: bca, cash, jago"
        string account_name "Nama Akun Rekening"
        number balance "Saldo Kas Tersedia"
        string type "liquid | investment"
        timestamp updated_at
    }

    EXPENSES {
        string id PK "UUID"
        string desc "Keterangan Belanja"
        number amount "Nominal Rupiah"
        string category "Kategori Transaksi"
        string type "Needs | Wants"
        timestamp date "Waktu Transaksi"
    }

    SHOPPING_ITEMS {
        string id PK "item slug / sanitized id"
        string item "Nama Barang"
        number qty "Jumlah Kebutuhan"
        string unit "Satuan (kg/liter/pack)"
        string category "Kategori Barang"
        boolean bought "Status Pembelian"
    }

    INVENTORY_ITEMS {
        string id PK "item slug"
        string item "Nama Bahan Makanan"
        number qty "Jumlah Stok Tersedia"
        string unit "Satuan"
        string category "Kategori Kulkas"
        timestamp updated_at
    }

    RECIPES {
        string id PK "recipe slug"
        string name "Judul Resep Masakan"
        string source_url "Link TikTok / YouTube"
        array ingredients "Daftar Bahan & Takaran"
        string steps "Langkah-Langkah Memasak"
        timestamp created_at
    }
```

---

## 🛠️ Tech Stack

- **AI Inference:** 9Router Proxy, DeepSeek V4 Flash, Mistral Medium, Google Gemini 2.5 Flash (Vision OCR).
- **Backend & Core Engine:** Python 3.11+, Unix Domain Sockets, `firebase-admin`, Google GenAI SDK.
- **Frontend Dashboard:** Next.js 16 (App Router, Standalone mode), React 19, TypeScript, Tailwind CSS v4, Lucide Icons, Recharts.
- **WhatsApp Bridge:** Node.js 20+ (Baileys library via Hermes Agent).
- **Database:** Google Cloud Firestore (GCP NoSQL).
- **Hosting & Infrastructure:** AWS EC2 (`t4g.micro` ARM64 Graviton, Ubuntu 24.04 LTS), Cloudflare Zero Trust Tunnel.

---

## 🚀 Panduan Setup & Instalasi

### 1. Prasyarat Sistem
- **Python:** Versi 3.11 atau lebih baru.
- **Node.js:** Versi 20.x atau lebih baru (`npm` atau `pnpm`).
- **Google Cloud Project:** Firestore aktif dan unduh service account JSON.
- **API Keys:** Google Gemini AI Studio key (untuk Vision OCR) dan/atau akun 9Router / DeepSeek / Mistral.

### 2. Kloning Repositori & Environment
```bash
git clone https://github.com/cantikapf/home-agent-template.git
cd home-agent-template

# Buat berkas environment backend
cp .env.example .env

# Letakkan service account GCP di folder root
cp /path/to/your-service-account.json firebase-credentials.json
```

### 3. Menjalankan Backend Python (Socket Daemon)
```bash
# Setup virtual environment & dependencies
python3 -m venv venv
source venv/bin/activate  # Di Windows: venv\Scripts\activate
pip install -r requirements.txt

# Jalankan daemon socket di background
python fast_daemon.py
```

### 4. Menjalankan Web Dashboard Next.js
```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```
Buka browser di `http://localhost:8501` untuk melihat dashboard keuangan, kulkas, dan daftar belanja.

---

## ⚙️ Referensi Environment Variables

| Variabel | Wajib? | Deskripsi | Contoh Nilai |
|---|:---:|---|---|
| `GEMINI_API_KEY` | **Ya** | API Key Google AI Studio untuk Vision OCR | `AIzaSyD...` |
| `NINEROUTER_URL` | Opsional | URL Proxy 9Router lokal atau remote | `http://localhost:20128/v1` |
| `FIREBASE_CREDENTIALS_PATH` | **Ya** | Path ke file service account JSON | `./firebase-credentials.json` |
| `HERMES_PYTHON` | Opsional | Path biner python untuk reminder worker | `/home/ubuntu/home-agent/venv/bin/python` |
| `PORT` | Opsional | Port untuk Web Dashboard Next.js | `8501` |

---

## 📱 TikTok Bulk Importer (Tutorial)

Bagi Anda yang memiliki puluhan atau ratusan video resep favorit di TikTok dan ingin menyalinnya otomatis ke database resep:

1. **Unduh Data TikTok:** Buka TikTok > *Pengaturan & Privasi* > *Akun* > *Unduh data Anda*. Pilih format **JSON**.
2. **Scan Resep:** Taruh file `user_data_tiktok.json` di folder `tiktok_data/`, lalu jalankan:
   ```bash
   python scripts/scan_tiktok_recipes.py
   ```
   Skrip ini memfilter video kuliner/resep berdasarkan kata kunci judul dalam waktu singkat.
3. **Ekstraksi AI Otomatis:** Jalankan:
   ```bash
   python scripts/import_tiktok_recipes.py
   ```
   Multimodal AI akan memproses video satu per satu dan menyimpan bahan serta instruksi ke Firestore secara otomatis dengan fitur *Auto-Resume*.

---

## 🔒 Keamanan & Sanitasi Kredensial

- Seluruh kredensial sensitif (`*.pem`, `*.key`, `*-credentials.json`, file API key, `.env`) diblokir ketat oleh `.gitignore`.
- Dashboard Next.js beroperasi secara *server-side* menggunakan `firebase-admin`, sehingga kredensial Firebase tidak pernah terekspos ke browser pengguna.

---

## 📄 Lisensi

Didistribusikan di bawah **MIT License**. Lihat berkas [LICENSE](LICENSE) untuk detail lengkap.

> **Catatan:** Proyek ini dibuat untuk otomatisasi urusan rumah tangga pribadi. Perhitungan keuangan dan rasio 50/30/20 disediakan untuk panduan praktis dan bukan nasihat keuangan profesional.

