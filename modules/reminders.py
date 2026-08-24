from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

def add_reminder(task, time_str, recurring=""):
    try:
        # User inputs local time string. Parse and convert to UTC.
        dt_local = dateutil.parser.parse(time_str)
        if dt_local.tzinfo is None:
            dt_local = dt_local.replace(tzinfo=datetime.now().astimezone().tzinfo)
        dt_utc = dt_local.astimezone(timezone.utc)
        
        doc_ref = db.collection('reminders').document()
        data = {
            'task': task,
            'time_str': dt_local.strftime('%Y-%m-%d %H:%M'),
            'timestamp': dt_utc,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        if recurring:
            data['recurring'] = recurring
            
        doc_ref.set(data)
        rec_str = f" (Berulang: {recurring})" if recurring else ""
        print(f"Pengingat berhasil disimpan: '{task}' pada waktu {dt_local.strftime('%d-%m-%Y %H:%M')}{rec_str}.")
        print("Beri tahu pengguna bahwa Anda akan mengingatkannya nanti secara otomatis.")
    except Exception as e:
        print(f"Format waktu gagal dipahami. Gagal menyimpan pengingat. Minta pengguna menyebutkan waktu spesifik YYYY-MM-DD HH:MM. Error: {e}")


def get_reminders():
    docs = db.collection('reminders').where('status', '==', 'pending').order_by('timestamp').stream()
    items = []
    for doc in docs:
        data = doc.to_dict()
        ts = data.get('timestamp')
        time_str = ts.astimezone().strftime('%d/%m/%Y %H:%M') if ts else data.get('time_str')
        items.append(f"- {time_str} : {data.get('task')}")
    
    if items:
        print("⏰ DAFTAR PENGINGAT AKTIF:")
        for item in items:
            print(item)
    else:
        print("Tidak ada pengingat yang sedang aktif.")


def delete_reminder(task_name):
    docs = db.collection('reminders').where('status', '==', 'pending').stream()
    deleted = False
    for doc in docs:
        data = doc.to_dict()
        if task_name.lower() in data.get('task', '').lower():
            doc.reference.delete()
            print(f"🗑️ Pengingat '{data.get('task')}' berhasil dibatalkan.")
            deleted = True
            break
    if not deleted:
        print(f"❌ Pengingat '{task_name}' tidak ditemukan.")

