from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

def _find_inventory_item_ref(item):
    # 1. Try original sanitize_id
    doc_ref = db.collection('inventory').document(sanitize_id(item))
    if doc_ref.get().exists:
        return doc_ref
        
    # 2. Try exact match on 'item' field
    docs = db.collection('inventory').where('item', '==', item).limit(1).get()
    if docs:
        return docs[0].reference
        
    # 3. Try exact item string as doc id (legacy)
    alt_ref = db.collection('inventory').document(item)
    if alt_ref.get().exists:
        return alt_ref
        
    return None
UNIT_CONVERSIONS = {
    'kg': {'base': 'gr', 'multiplier': 1000},
    'gr': {'base': 'gr', 'multiplier': 1},
    'gram': {'base': 'gr', 'multiplier': 1},
    'liter': {'base': 'ml', 'multiplier': 1000},
    'l': {'base': 'ml', 'multiplier': 1000},
    'ml': {'base': 'ml', 'multiplier': 1},
    'lusin': {'base': 'pcs', 'multiplier': 12},
    'pcs': {'base': 'pcs', 'multiplier': 1}
}

def convert_unit(qty, from_unit, to_unit):
    if not from_unit or not to_unit:
        return qty
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit == to_unit:
        return qty
    
    if from_unit in UNIT_CONVERSIONS and to_unit in UNIT_CONVERSIONS:
        from_info = UNIT_CONVERSIONS[from_unit]
        to_info = UNIT_CONVERSIONS[to_unit]
        if from_info['base'] == to_info['base']:
            # Convert to base first, then to target
            base_qty = qty * from_info['multiplier']
            return base_qty / to_info['multiplier']
            
    return qty  # Return as-is if no conversion possible

def update_inventory(item, qty, action, unit="", category=""):
    if qty < 0:
        print("Error: Kuantitas tidak boleh negatif.")
        return
    
    if action not in ('add', 'use'):
        print(f"Error: Action '{action}' tidak valid. Gunakan 'add' atau 'use'.")
        return
        
    doc_ref = _find_inventory_item_ref(item)
    if not doc_ref:
        doc_ref = db.collection('inventory').document(sanitize_id(item))
    
    doc = doc_ref.get()
    
    current_qty = doc.to_dict().get('quantity', 0) if doc.exists else 0
    current_unit = doc.to_dict().get('unit', '') if doc.exists else unit
    
    # Konversi satuan jika beda
    if doc.exists and unit and unit.lower() != current_unit.lower():
        qty = convert_unit(qty, unit, current_unit)
        unit = current_unit # Pakai satuan yang sudah ada di database
    
    # Cek stok saat ini jika action == 'use' untuk mencegah stok negatif
    if action == 'use':
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


def get_inventory():
    docs = db.collection('inventory').stream()
    items = []
    for doc in docs:
        data = doc.to_dict()
        item_name = data.get('item', '')
        qty = data.get('quantity', 0)
        unit = data.get('unit', '')
        unit_str = f" {unit}" if unit else ""
        items.append(f"- {item_name}: {qty}{unit_str}")
    
    if items:
        print("📦 Daftar Stok Saat Ini:")
        for item in items:
            print(item)
    else:
        print("Stok masih kosong.")



def update_category(item, new_category):
    doc_ref = _find_inventory_item_ref(item)
    doc = doc_ref.get() if doc_ref else None
    
    if doc and doc.exists:
        doc_ref.update({'category': new_category})
        print(f"✅ Kategori stok {item} berhasil diubah menjadi '{new_category}'.")
    else:
        # Coba update di shopping list
        from .shopping import _find_shopping_item_ref
        shop_ref = _find_shopping_item_ref(item)
        if shop_ref and shop_ref.get().exists:
            shop_ref.update({'category': new_category})
            print(f"✅ Kategori daftar belanja {item} berhasil diubah menjadi '{new_category}'.")
        else:
            print(f"❌ Barang '{item}' tidak ditemukan di stok kulkas maupun daftar belanja.")

def delete_stock(item):
    doc_ref = _find_inventory_item_ref(item)
    if doc_ref and doc_ref.get().exists:
        doc_ref.delete()
        print(f"✅ Item '{item}' berhasil dihapus sepenuhnya dari database stok kulkas.")
    else:
        print(f"⚠️ Item '{item}' tidak ditemukan di stok kulkas.")

