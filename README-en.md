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
  <b>An autonomous AI-powered household operating system operating via WhatsApp and a real-time Next.js 16 web dashboard.</b><br />
  Instant receipt OCR (Vision AI), real cash flow tracking with Zero-Budgeting (50/30/20 Wants Rule), pantry inventory management, and automated TikTok/YouTube recipe ingestion.
</p>

<p align="center">
  <a href="README.md">Baca dalam Bahasa Indonesia</a> • <a href="README-en.md"><b>English</b></a>
</p>

---

## 📸 Interface & System Preview

| **Finance & Cash Flow (`/finance`)** | **System Overview & Health (`/`)** |
|:---:|:---:|
| ![Finance Dashboard Preview](docs/assets/dashboard-preview.svg) | ![System Overview Preview](docs/assets/system-overview.svg) |

<p align="center">
  <b>WhatsApp Assistant Interaction (Vision OCR Receipt &amp; Cooking Recipes):</b><br />
  <img src="docs/assets/whatsapp-chat.svg" alt="WhatsApp Chat Preview" width="560px" />
</p>

---

## ✨ Core Features

- 🧾 **Snap a Receipt (Vision AI):** Too lazy to manually log every expense? Just send a photo of your receipt on WhatsApp. Google Gemini 2.5 Flash reads line items, calculates totals, and categorizes transactions instantly.
- 💰 **Zero-Budgeting & 50/30/20 Wants Rule:** Eliminates rigid, unrealistic monthly budgets. Financial health centers on **Liquid Available Cash**. Impulsive lifestyle spending (*Wants*) is strictly monitored under a 30% monthly ratio with proactive spending alerts.
- ❄️ **Smart Fridge & Pantry Management:** Track perishable food items with dynamic units (pieces, kg, liters), low-stock alerts, and auto-deduction when preparing recipes.
- 🛒 **Integrated Shopping List:** Queue shopping items. When items are purchased (`ha --action bought`), the system automatically logs the expense, auto-deducts liquid cash, and moves items to fridge inventory. Supports Tokopedia and Shopee OpenGraph link extraction.
- 🍳 **Multimodal Video Recipe Extractor:** Send a TikTok or YouTube cooking video link. The multimodal AI watches the video, extracting ingredients and step-by-step cooking steps directly into your recipe collection.
- ⏰ **Smart Reminders & Weekly Briefings:** Set one-time or recurring reminders (*daily/weekly/monthly*). Every Sunday evening, the assistant sends an automated cash flow summary directly to WhatsApp.
- ⚡ **Zero Cold-Start Python Daemon:** In-memory Unix domain socket architecture keeps Firestore connections and Python modules warm in server memory for sub-second execution times.
- 🔀 **Multi-Tier AI Brain (9Router Gateway):** 3-tier intelligent fallback routing (**DeepSeek V4 Flash** primary ➔ **Mistral Medium** fallback 1 ➔ **Gemini 2.5 Flash** fallback 2) ensures 99.9% uptime at near-zero inference cost.

---

## 📊 Architecture & Workflow Visualizations

### 1. Request Lifecycle
End-to-end user request flow from WhatsApp to Firestore mutations and back:

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

    User->>GW: Send Message / Receipt Photo / Recipe Link
    alt Grocery Receipt Photo
        GW->>Router: Forward Vision Payload (Gemini 2.5 Flash)
        Router-->>GW: Structured OCR Data (Items, Total, Category)
    else Text Prompt
        GW->>Router: Chat Completion Request
        Router->>LLM: 3-Tier Failover (DeepSeek ➔ Mistral ➔ Gemini)
        LLM-->>Router: Tool Calling Decision (CLI ha)
        Router-->>GW: Forward Tool Call
    end
    GW->>CLI: Execute Tool (ha --action ...)
    CLI->>Daemon: Send IPC via Unix Domain Socket (/tmp/home_agent.sock)
    Daemon->>DB: Mutate Documents / Auto-deduct Liquid Cash
    DB-->>Daemon: Snapshot Confirmation
    Daemon-->>CLI: Return JSON Execution Status
    CLI-->>GW: Formatted Output
    GW->>User: Reply to WhatsApp (Clean Emoji Bullet Points)
```

---

### 2. Server Infrastructure & Port Topology
Background processes on AWS EC2 Graviton connected via Cloudflare Zero Trust:

```mermaid
flowchart TD
    subgraph Clients ["Client Layer"]
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

    subgraph CloudServices ["External Cloud & AI Services"]
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

    HGW -->|Invoke CLI `ha`| FDaemon
    RemWorker -->|Polling & Cron| Firestore
    RemWorker -->|Send WA Message| HGW
    FDaemon -->|Query & Mutate| Firestore
    WebDash -->|Server-side firebase-admin| Firestore

    classDef client fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef server fill:#f8fafc,stroke:#475569,stroke-width:2px,color:#0f172a;
    classDef cloud fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#0f172a;
    class WA,Browser client;
    class HGW,WebDash,NineR,FDaemon,RemWorker,CFD server;
    class DeepSeek,Mistral,Gemini,Firestore cloud;
```

---

### 3. AI Fallback & Token Saver Architecture (9Router)
Multi-provider defense chain to eliminate downtime and rate limits:

```mermaid
graph TD
    Request([📥 Chat / Tool Call Request]) --> NineRouter[🔀 9Router Proxy Gateway]
    
    subgraph ComboBrain ["hermes-fallback (Text & CLI Tool Calling)"]
        NineRouter -->|Tier 1 - Ultra Cost-Efficient| DeepSeek["🟢 DeepSeek V4 Flash (Primary)"]
        DeepSeek -.->|On HTTP 429 / 5xx| Mistral["🟠 Mistral Medium (Fallback 1)"]
        Mistral -.->|On Quota Depletion| GeminiChat["🔵 Gemini 2.5 Flash (Fallback 2)"]
    end

    subgraph VisionPipeline ["Image & Receipt Adapter"]
        NineRouter -->|Detects base64 image / URL| GeminiVision["🟣 Gemini 2.5 Flash Vision Direct"]
    end

    subgraph OptimizationLayer ["Token Savers & Caching"]
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

### 4. Data Entity Schema (Firestore Collections)
NoSQL collection architecture linking expenses, pantry, cash, and recipes:

```mermaid
erDiagram
    ASSETS ||--o{ EXPENSES : "auto-deducts on transaction"
    SHOPPING_ITEMS }o--|| INVENTORY_ITEMS : "transfers stock when bought"
    RECIPES ||--o{ INVENTORY_ITEMS : "suggests menu from stock"

    ASSETS {
        string id PK "e.g. bca, cash, savings"
        string account_name "Account Name"
        number balance "Liquid Available Cash"
        string type "liquid | investment"
        timestamp updated_at
    }

    EXPENSES {
        string id PK "UUID"
        string desc "Expense Description"
        number amount "Amount"
        string category "Transaction Category"
        string type "Needs | Wants"
        timestamp date "Transaction Timestamp"
    }

    SHOPPING_ITEMS {
        string id PK "item slug / sanitized id"
        string item "Item Name"
        number qty "Requested Quantity"
        string unit "Unit (kg/liter/pack)"
        string category "Item Category"
        boolean bought "Purchase Status"
    }

    INVENTORY_ITEMS {
        string id PK "item slug"
        string item "Ingredient Name"
        number qty "Available Stock"
        string unit "Unit"
        string category "Pantry Category"
        timestamp updated_at
    }

    RECIPES {
        string id PK "recipe slug"
        string name "Recipe Title"
        string source_url "TikTok / YouTube URL"
        array ingredients "Ingredients & Measurements"
        string steps "Step-by-step Instructions"
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

## 🚀 Setup & Installation Guide

### 1. System Prerequisites
- **Python:** Version 3.11 or later.
- **Node.js:** Version 20.x or later (`npm` or `pnpm`).
- **Google Cloud Project:** Firestore activated with a downloaded Service Account JSON.
- **API Keys:** Google Gemini AI Studio key (for Vision OCR) and/or 9Router / DeepSeek / Mistral credentials.

### 2. Clone Repository & Configure Environment
```bash
git clone https://github.com/cantikapf/home-agent-template.git
cd home-agent-template

# Create backend environment file
cp .env.example .env

# Place your GCP service account JSON in the root directory
cp /path/to/your-service-account.json firebase-credentials.json
```

### 3. Run Python Backend (Socket Daemon)
```bash
# Setup virtual environment & dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Launch socket daemon in the background
python fast_daemon.py
```

### 4. Run Next.js Web Dashboard
```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```
Open your browser at `http://localhost:8501` to view your real-time financial cash flow, fridge inventory, and shopping list.

---

## ⚙️ Environment Variables Reference

| Variable | Required? | Description | Example |
|---|:---:|---|---|
| `GEMINI_API_KEY` | **Yes** | Google AI Studio Key for Vision OCR | `AIzaSyD...` |
| `NINEROUTER_URL` | Optional | Local or remote 9Router proxy URL | `http://localhost:20128/v1` |
| `FIREBASE_CREDENTIALS_PATH` | **Yes** | Path to service account JSON key | `./firebase-credentials.json` |
| `HERMES_PYTHON` | Optional | Python binary path for reminder scheduler | `/home/ubuntu/home-agent/venv/bin/python` |
| `PORT` | Optional | Port for Next.js Web Dashboard | `8501` |

---

## 📱 TikTok Bulk Importer (Tutorial)

If you have dozens or hundreds of recipe bookmarks on TikTok and want to automatically import them:

1. **Request TikTok Data:** Go to TikTok > *Settings and Privacy* > *Account* > *Download your data*. Select **JSON** format.
2. **Scan Recipes:** Place `user_data_tiktok.json` in the `tiktok_data/` folder and run:
   ```bash
   python scripts/scan_tiktok_recipes.py
   ```
   This script rapidly scans and filters cooking recipes based on title keywords.
3. **Automated AI Extraction:** Run:
   ```bash
   python scripts/import_tiktok_recipes.py
   ```
   The Multimodal AI sequentially reads the videos, saving ingredients and cooking steps directly to Firestore with built-in *Auto-Resume*.

---

## 🔒 Security & Privacy Notice

- Sensitive credentials (`*.pem`, `*.key`, `*-credentials.json`, API key files, `.env`) are strictly excluded by `.gitignore`.
- The Next.js dashboard uses server-side data fetching via `firebase-admin`, preventing Firebase service account exposure to client browsers.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more details.

> **Disclaimer:** This project is designed for personal household automation. Financial calculations and the 50/30/20 ratio are provided for informational tracking and do not constitute professional financial advice.

