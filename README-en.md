# 🏡 Home Agent (WhatsApp Personal Assistant)

*[Baca dalam Bahasa Indonesia](README.md)*

Home Agent is an AI-powered personal assistant I built to handle those trivial-yet-important household chores, right from WhatsApp.

Tired of checking an empty fridge? Too lazy to type out a recipe from a TikTok video? Or maybe you just want to track your daily expenses by snapping a photo of your grocery receipt? Well, this bot does all of that for you.

## ✨ Key Features

- 🛒 **Smart Shopping List:** It doesn't just take notes. Send a link from Shopee or Tokopedia, and the bot will automatically extract the product name for you.
- 🧾 **Snap a Receipt (Vision AI):** Too lazy to log expenses one by one? Just snap a photo of your grocery receipt. The AI will read the prices, calculate the total, and categorize the expense automatically.
- ❄️ **Fridge & Pantry Management:** Keep track of your food stock in real-time.
- 🍳 **Smart Recipe Book & Video Extractor:** Got a recipe video from TikTok or YouTube? Just send the link. The Multimodal AI will watch it and save the ingredients and cooking steps straight into your recipe database.
- 💰 **Comprehensive Finance Management:** Track daily/weekly expenses, log recurring monthly bills (Bills), and track your savings/liquid investments (Assets). Every time you log an expense, the bot tells you your remaining budget.
- ⏰ **Smart Reminders:** Set one-time or recurring reminders right from WhatsApp. Plus, the bot automatically sends weekly finance reports.
- 🤖 **Agnostic AI Engine:** Powered by Hermes Gateway, allowing it to use Mistral (super fast & efficient) for main logic and Gemini for Vision/Multimodal tasks.

## 📊 How Does It Work? (Architecture)

To prevent slow replies and *cold starts*, I built the architecture using a *socket daemon*. This keeps Firebase and the AI models on standby in the server's memory. When a chat comes in, execution is lightning-fast!

```mermaid
sequenceDiagram
    participant User as 📱 WhatsApp (User)
    participant Hermes as 🤖 Hermes Agent (Node.js)
    participant CLI as ⌨️ Fast CLI (Python)
    participant Daemon as ⚙️ Fast Daemon (Socket)
    participant Gemini as 🧠 Gemini AI (Multimodal)
    participant Firebase as 🗄️ Firestore (Database)

    User->>Hermes: Chat / Photo / Video
    Hermes->>Gemini: Understand intent & extract instructions
    Gemini-->>Hermes: Determine Tool (e.g., "Log Milk Purchase")
    Hermes->>CLI: Execute Tool (fast_cli.py --action shopping --item Milk)
    CLI->>Daemon: Send via Unix Socket (Instant)
    Daemon->>Firebase: Save "Milk" to database
    Firebase-->>Daemon: Success
    Daemon-->>CLI: Return result
    CLI-->>Hermes: Tool execution output
    Hermes->>User: Reply WA ("Milk logged successfully! ✅")
```

## 🛠️ Tech Stack

- **AI Engine:** Google Gemini (Gemini 2.5 Flash & Flash-Lite) handled by the **Hermes Agent** framework.
- **WhatsApp Bridge:** Node.js (via Baileys).
- **Database:** Firebase Firestore (GCP).
- **Hosting:** Oracle Cloud VPS (Ubuntu).
- **CI/CD:** GitHub Actions.

## 🚀 CI/CD Pipeline (Auto-Deploy)

Whenever code changes are pushed to the `main` branch, GitHub Actions automatically triggers a runner to SSH into the VPS, pull the latest code, and restart the bot service. No more tedious manual SSH just to update a feature.

## 🔒 Security & Credentials Setup

Don't worry, sensitive data like `.env`, Firebase `.json` credentials, and SSH `.key` files are securely blocked by `.gitignore`.

If you want to run or fork this bot locally:
1. Copy `.env.example` to `.env` and insert your Gemini API Key.
2. Place your Firebase service account file (`firebase-credentials.json`) in the root folder.
3. Set up and run the Python daemon!
