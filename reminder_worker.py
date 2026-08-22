import os
import time
import subprocess
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timezone

# Gunakan absolute path agar aman jika dijalankan via systemd/cron
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')

cred = credentials.Certificate(CRED_PATH)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def send_whatsapp_message(msg):
    # Menggunakan path hermes_cli module secara eksplisit
    python_bin = os.environ.get('HERMES_PYTHON', os.path.join(os.path.expanduser('~'), '.hermes', 'hermes-agent', 'venv', 'bin', 'python'))
    # jika hermes-agent tidak ditemukan, mungkin di tempat lain
    if not os.path.exists(python_bin):
        print(f"Error: Python binary for hermes not found at {python_bin}")
        return
        
    cmd = [python_bin, '-m', 'hermes_cli.main', 'send', '--to', 'whatsapp', msg]
    cwd_path = os.path.join(os.path.expanduser('~'), '.hermes', 'hermes-agent')
    subprocess.run(cmd, cwd=cwd_path)

def check_reminders():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for reminders...")
    # Bandingkan dengan waktu saat ini (UTC aware) karena di Firestore menggunakan SERVER_TIMESTAMP (UTC)
    now_utc = datetime.now(timezone.utc)
    
    # Ambil pengingat yang pending dan waktunya sudah lewat atau sama dengan sekarang
    docs = db.collection('reminders')\
        .where('status', '==', 'pending')\
        .where('timestamp', '<=', now_utc)\
        .stream()
        
    for doc in docs:
        data = doc.to_dict()
        task = data.get('task', 'Tanpa Nama')
        
        # Kirim pesan via Hermes
        msg = f"⏰ *PENGINGAT* ⏰\n\nHalo! Waktunya untuk: \n*{task}*"
        send_whatsapp_message(msg)
        
        # Update status menjadi 'done'
        doc.reference.update({
            'status': 'done',
            'notified_at': firestore.SERVER_TIMESTAMP
        })
        print(f"Reminded: {task}")

if __name__ == '__main__':
    while True:
        try:
            check_reminders()
        except Exception as e:
            print(f"Error checking reminders: {e}")
        
        # Cek setiap 60 detik
        time.sleep(60)
