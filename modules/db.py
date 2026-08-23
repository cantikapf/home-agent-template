import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')
cred = credentials.Certificate(CRED_PATH)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def get_now_utc():
    return datetime.now(timezone.utc)

def sanitize_id(item_name):
    return item_name.replace('/', '-').lower()
