# 🏡 Home Agent (WhatsApp Personal Assistant)

*Baca terjemahan dalam [Bahasa Indonesia](README.md)*

Welcome to the **Home Agent** repository, a smart AI-powered home assistant integrated directly with your WhatsApp (via [Hermes Agent](https://github.com/cantikapf/hermes-agent)).

This project was built to automate daily household chores, from monitoring fridge inventory, tracking financial expenses, to extracting cooking recipes directly from TikTok videos using *Multimodal AI*.

## ✨ Key Features

- 🛒 **Shopping List Management:** Add and record items you need to buy.
- 📦 **Fridge & Kitchen Inventory:** Real-time monitoring of food ingredients. The AI will notify you if you are running out of stock for a specific recipe.
- 🍳 **Smart Recipe Book:** Save your favorite recipes. The AI can suggest recipes based on the ingredients currently available in your fridge!
- 🎥 **TikTok Recipe Extraction:** A superpower feature that "watches" TikTok recipe videos using *Multimodal AI* (Gemini), extracts the ingredients and cooking steps, and saves them to your Recipe Book.
- 💸 **Expense Tracking:** Monitor your daily and weekly household expenses effortlessly.

## 🛠️ Prerequisites

To run this project on your machine, you will need:

1. **Python 3.10+** installed on your system.
2. **Hermes Agent** (or a similar WhatsApp bot framework that supports command-line tool execution).
3. **Google Gemini API Key** (Free from Google AI Studio).
4. **Firebase Firestore Database** (Free tier on Google Cloud/Firebase).
   - Create a new Firebase project.
   - Initialize a Firestore Database.
   - Generate a *Service Account Key* (Settings > Service Accounts > Generate new private key).

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/cantikapf/home-agent-template.git
   cd home-agent-template
   ```

2. **Run the Setup Script:**
   This script will install all dependencies and dynamically replace configuration paths to match your current directory.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Credentials:**
   - Rename your Firebase Service Account Key file to `firebase-credentials.json` and place it in the root of this project.
   - Open the `.env` file and insert your `GEMINI_API_KEY`.

4. **Integrate with Hermes Agent:**
   - A `skills/` folder will be generated (containing Markdown instructions for the AI).
   - Move or copy the contents of this `skills/` folder to your Hermes bot's skills directory (e.g., `~/.hermes/skills/home-agent/`).

5. **Run the Socket Daemon:**
   This project uses a lightning-fast *socket daemon* (`fast_daemon.py`) so the Python model and Firebase libraries don't have to reload on every incoming WhatsApp message.
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   # Run the daemon
   python fast_daemon.py
   ```
   *(It is highly recommended to run this daemon via `systemd` or `pm2` to keep it running in the background).*

## 🏗️ Architecture

- `home_agent.py`: Contains all business logic (Firestore CRUD, Gemini Vision integration, etc.).
- `fast_daemon.py`: A Unix socket server that loads `home_agent.py` into memory, making command execution significantly faster by eliminating cold-start overhead.
- `fast_cli.py`: A lightweight CLI client called by Hermes Agent. It forwards terminal arguments to the daemon via the socket.
- `reminder_worker.py`: A background worker that polls Firestore for scheduled reminders every 60 seconds.
- `skills_template/`: Prompt templates for the AI. This is converted into the `skills/` directory when running `setup.sh`.

## 🤝 Contributing

Feel free to open an *Issue* or submit a *Pull Request* if you find bugs or want to add new features! Community contributions are highly welcomed.

## 📄 License
[MIT License](LICENSE)
