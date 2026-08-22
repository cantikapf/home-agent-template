# 🏡 Home Agent (WhatsApp Personal Assistant)

*Baca terjemahan dalam [Bahasa Indonesia](README.md)*

Welcome to the **Home Agent** repository, a smart AI-powered home assistant integrated directly with your WhatsApp (via [Hermes Agent](https://github.com/cantikapf/hermes-agent)).

This project was built to automate daily household chores, from monitoring fridge inventory, tracking financial expenses, to extracting cooking recipes directly from TikTok videos using *Multimodal AI*.

## ✨ Comprehensive Features

🤖 **AI & Automation System**
- **Multimodal AI:** Integrated with Gemini Vision to analyze images and videos.
- **Fast Daemon:** Uses a Unix Socket Server (`fast_daemon.py`) for lightning-fast AI responses without cold-starting Python/Firebase.
- **Auto-Shopping List:** Automatically adds items to your shopping list when kitchen stock runs low (≤ 2).
- **Automated Reports:** Sends a weekly financial summary automatically every Sunday at 19:00.

💸 **Financial Management**
- Record daily expenses with descriptions and categories.
- Set monthly budget limits.
- Check remaining balance and budget usage percentages.
- View expense summaries for the current or previous months.
- **Undo/Delete:** Cancel or delete an expense if you made a typo.

📦 **Fridge & Kitchen Inventory**
- Monitor grocery stocks (add/use) in *real-time*.
- Check the availability of all kitchen items in one command.
- **Smart Combo:** When you report "I bought [item]", the bot automatically does 3 things: crosses it off the shopping list, adds it to the kitchen stock, and records it as an expense.

🛒 **Shopping List**
- Add and remove items from the shopping list.
- View pending items you need to buy.
- Clear the cart of already purchased items.

🍳 **Recipe Book & TikTok**
- **TikTok Recipe Extraction:** Send a TikTok cooking video URL, and the AI will "watch" it to extract the ingredients and steps!
- Save favorite recipes to your Recipe Book database.
- View and re-read recipe details.
- Delete recipes you no longer like.
- **AI Chef:** Ask the AI to brainstorm creative cooking ideas based on leftover ingredients in your fridge.

⏰ **Reminders**
- Schedule alarms for household chores (e.g., "remind me to buy electricity tokens tomorrow at 10 AM").
- View a list of all active/pending reminders.
- Cancel reminders that are no longer needed.

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
