import os
import time
import json
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
        try:
            send_whatsapp_message(msg)

            # Update status menjadi 'done' HANYA jika pesan berhasil terkirim
            doc.reference.update({
                'status': 'done',
                'notified_at': firestore.SERVER_TIMESTAMP
            })
            print(f"Reminded: {task}")
            
            # Cek jika ini adalah recurring reminder
            recurring = data.get('recurring', '').lower()
            if recurring:
                try:
                    from datetime import timedelta
                    from dateutil.relativedelta import relativedelta
                    
                    old_timestamp = data.get('timestamp')
                    # Parse local datetime from time_str
                    from dateutil.parser import parse as date_parse
                    dt_local = date_parse(data.get('time_str'))
                    
                    if 'daily' in recurring or 'hari' in recurring:
                        next_time = dt_local + timedelta(days=1)
                    elif 'weekly' in recurring or 'minggu' in recurring:
                        next_time = dt_local + timedelta(days=7)
                    elif 'monthly' in recurring or 'bulan' in recurring:
                        next_time = dt_local + relativedelta(months=1)
                    else:
                        print(f"⚠️ Recurring type '{recurring}' tidak dipahami, skip perpanjangan.")
                        continue
                        
                    next_utc = next_time.astimezone(timezone.utc)
                    new_doc = db.collection('reminders').document()
                    new_doc.set({
                        'task': task,
                        'time_str': next_time.strftime('%Y-%m-%d %H:%M'),
                        'timestamp': next_utc,
                        'status': 'pending',
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'recurring': recurring
                    })
                    print(f"♻️ Auto-renewed recurring reminder: {task} untuk {next_time.strftime('%Y-%m-%d %H:%M')}")
                except Exception as ex:
                    print(f"Error auto-renewing reminder: {ex}")

        except Exception as e:
            # Jika gagal kirim, biarkan tetap pending agar dicoba lagi nanti
            print(f"Gagal mengirim reminder '{task}': {e}. Akan dicoba lagi nanti.")

def send_weekly_report():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sending automatic weekly report...")
    # Panggil get_weekly_report dari home_agent via hermes-agent CLI
    # Untuk lebih mudah, kita jalankan home_agent.py di terminal, tangkap outputnya, lalu kirim via WA
    try:
        import subprocess
        python_bin = os.path.join(BASE_DIR, 'venv', 'bin', 'python')
        if not os.path.exists(python_bin):
            python_bin = 'python3'
            
        home_agent_script = os.path.join(BASE_DIR, 'home_agent.py')
        result = subprocess.run([python_bin, home_agent_script, '--action', 'weekly_report'], capture_output=True, text=True)
        if result.returncode == 0:
            send_whatsapp_message(result.stdout)
            print("Weekly report sent successfully.")
        else:
            print(f"Failed to generate weekly report: {result.stderr}")
    except Exception as e:
        print(f"Error sending weekly report: {e}")

if __name__ == '__main__':
    # Simpan state ke file agar tahan restart
    STATE_FILE = os.path.join(BASE_DIR, '.reminder_state.json')
    
    def load_state():
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_state(state):
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    
    state = load_state()
    last_weekly_report_date = state.get('last_weekly_report_date', None)
    
    while True:
        try:
            check_reminders()
            
            # Cek Laporan Mingguan (Minggu jam 19:00)
            now_local = datetime.now().astimezone()
            if now_local.weekday() == 6 and now_local.hour == 19: # 6 = Minggu
                current_date = now_local.strftime('%Y-%m-%d')
                if last_weekly_report_date != current_date:
                    send_weekly_report()
                    last_weekly_report_date = current_date
                    save_state({'last_weekly_report_date': current_date})
                    
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        # Cek setiap 60 detik
        time.sleep(60)
