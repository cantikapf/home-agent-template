from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

def update_inventory(item, qty, action, unit="", category=""):
    if qty < 0:
        print("Error: Kuantitas tidak boleh negatif.")
        return
    
    if action not in ('add', 'use'):
        print(f"Error: Action '{action}' tidak valid. Gunakan 'add' atau 'use'.")
        return
        
    doc_ref = db.collection('inventory').document(sanitize_id(item))
    
    # Cek stok saat ini jika action == 'use' untuk mencegah stok negatif
    if action == 'use':
        doc = doc_ref.get()
        current_qty = doc.to_dict().get('quantity', 0) if doc.exists else 0
        if current_qty <= 0:
            print(f"⚠️ Stok {item} sudah habis (0). Tidak ada yang bisa dikurangi.")
            return
        if current_qty < qty:
            print(f"⚠️ Stok {item} tidak cukup. Saat ini hanya ada {current_qty}. Dikurangi menjadi 0.")
            qty = current_qty  # Kurangi hanya sampai 0
    
    inc_val = float(qty) if action == 'add' else -float(qty)
    data = {'item': item, 'updated_at': firestore.SERVER_TIMESTAMP, 'quantity': firestore.Increment(inc_val)}
    if unit: data['unit'] = unit
    if category: data['category'] = category
    doc_ref.set(data, merge=True)
    
    # Fetch immediately to get the updated stock
    doc = doc_ref.get()
    new_qty = doc.to_dict().get('quantity', 0)
    final_unit = doc.to_dict().get('unit', unit)
    
    unit_str = f" {final_unit}" if final_unit else ""
    print(f"Stok {item} berhasil diperbarui. Stok saat ini: {new_qty}{unit_str}")
    if new_qty <= 2:
        shop_ref = db.collection('shopping_list').document(sanitize_id(item))
        if not shop_ref.get().exists:
            data_auto = {'item': item, 'quantity': 1, 'unit': final_unit, 'status': 'pending'}
            if category: data_auto['category'] = category
            shop_ref.set(data_auto)
            print(f"🤖 (Auto-System): {item} otomatis ditambahkan ke daftar belanja karena stok menipis (≤2).")
    
    if new_qty <= 0:
        print(f"PENGUMUMAN: Stok {item} sudah habis! Beritahu pengguna bahwa item telah ditambahkan ke daftar belanja.")
    elif new_qty <= 2:
        print(f"⚠️ PERHATIAN: Stok {item} tinggal sedikit ({new_qty}{unit_str}).")


def get_inventory():
    docs = db.collection('inventory').stream()
    items = []
    low_stock = []
    for doc in docs:
        data = doc.to_dict()
        item_name = data.get('item', '')
        qty = data.get('quantity', 0)
        unit = data.get('unit', '')
        unit_str = f" {unit}" if unit else ""
        items.append(f"- {item_name}: {qty}{unit_str}")
        if qty <= 2 and qty > 0:
            low_stock.append(item_name)
        elif qty <= 0:
            low_stock.append(f"{item_name} (HABIS!)")
    
    if items:
        print("📦 Daftar Stok Saat Ini:")
        for item in items:
            print(item)
        if low_stock:
            print(f"\n⚠️ Stok hampir habis/habis: {', '.join(low_stock)}")
    else:
        print("Stok masih kosong.")

