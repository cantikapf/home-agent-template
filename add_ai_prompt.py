import os
import re

PUBLIC_DIR = r"D:\PERSONAL PROJECT\Home Agent Public"
readme_id_path = os.path.join(PUBLIC_DIR, "README.md")
readme_en_path = os.path.join(PUBLIC_DIR, "README-en.md")

ai_section_id = """
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

## 🏗️ Arsitektur"""

ai_section_en = """
## 🪄 Automated Installation via AI (Cursor, Claude, Antigravity)
Don't want to set things up manually? If you use an *AI Coding Assistant* like **Cursor**, **Claude**, **Windsurf**, or **Google Antigravity**, just copy and paste the prompt below into your AI chat and let it do the heavy lifting:

```text
Please help me install the Home Agent project from https://github.com/cantikapf/home-agent-template.git.
1. Clone the repository into this directory.
2. Create a virtual environment, activate it, and install dependencies from requirements.txt.
3. Make setup.sh executable (chmod +x) and run it.
4. Guide me on how to get my Firebase Service Account Key and Gemini API key, then wait for my input.
5. Once I provide them, create the firebase-credentials.json and .env files for me.
6. Finally, run `fast_daemon.py` in the background and verify there are no errors.
```

## 🏗️ Architecture"""

with open(readme_id_path, 'r', encoding='utf-8') as f:
    content_id = f.read()
content_id = content_id.replace("## 🏗️ Arsitektur", ai_section_id)
with open(readme_id_path, 'w', encoding='utf-8') as f:
    f.write(content_id)

with open(readme_en_path, 'r', encoding='utf-8') as f:
    content_en = f.read()
content_en = content_en.replace("## 🏗️ Architecture", ai_section_en)
with open(readme_en_path, 'w', encoding='utf-8') as f:
    f.write(content_en)

print("AI Installation sections injected successfully.")
