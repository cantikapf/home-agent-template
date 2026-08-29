import json
from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

from .finance import add_expense, get_balance, get_current_month_str, get_month_bounds, _auto_adjust_liquid_asset, get_current_cash_balance, is_wants_expense
from .inventory import update_inventory
def add_shopping_list(item, qty, unit="", category=""):
    if qty < 0:
        print("Error: Kuantitas tidak boleh negatif.")
        return
        
    # Auto-extract from URL if item is a link
    import re
    url_match = re.search(r'(https?://[^\s]+)', item)
    if url_match:
        original_url = url_match.group(1)
        item = original_url
        print(f"Mendeteksi URL, mencoba mengekstrak nama barang dari {original_url}...")
        try:
            import urllib.request, urllib.parse, re
            req = urllib.request.Request(item, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=15)
            final_url = response.geturl()
            
            html = response.read().decode('utf-8')
            
            # 1. Coba ambil dari og:title (Sering ada di Shopee / Tokopedia SPA)
            match_og = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            # Kadang urutannya content dulu baru property
            if not match_og:
                match_og = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']', html, re.IGNORECASE)
            
            if match_og:
                item = match_og.group(1).strip()
                # Bersihkan embel-embel SEO
                item = item.replace(' | Shopee Indonesia', '').replace(' | Tokopedia', '')
                if item.startswith('Jual '):
                    item = item[5:]
            else:
                # 2. Fallback ke regex URL Shopee (jika ada slug)
                if 'shopee' in final_url or 'shp.ee' in final_url:
                    match_slug = re.search(r'shopee\.co\.id/([^/]+)-i\.\d+', final_url)
                    if match_slug:
                        item = urllib.parse.unquote(match_slug.group(1)).replace('-', ' ')
                # 3. Fallback ke regex URL Tokopedia
                elif 'tokopedia.com' in final_url:
                    match_slug = re.search(r'tokopedia\.com/[^/]+/([^/?]+)', final_url)
                    if match_slug:
                        item = urllib.parse.unquote(match_slug.group(1)).replace('-', ' ')
                # 4. Fallback ke tag <title> biasa
                else:
                    match_title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    if match_title:
                        item = match_title.group(1).strip()
                    else:
                        item = f"Barang dari Link ({uuid.uuid4().hex[:6]})"
                        
            # Tambahkan penanda platform untuk kejelasan daftar belanja
            if 'shopee' in final_url.lower() and '(Shopee)' not in item:
                item += " (Shopee)"
            elif 'tokopedia' in final_url.lower() and '(Tokopedia)' not in item:
                item += " (Tokopedia)"
        except Exception as e:
            print(f"Gagal mengekstrak link: {e}")
            item = f"Barang dari Link ({uuid.uuid4().hex[:6]})"

    doc_ref = db.collection('shopping_list').document(sanitize_id(item))
    data = {'item': item, 'quantity': qty, 'status': 'pending'}
    if unit: data['unit'] = unit
    if category: data['category'] = category
    if 'http' in str(item) or 'Barang dari Link' in item or '(Shopee)' in item or '(Tokopedia)' in item:
        # Jika berhasil di ekstrak, simpan url aslinya
        data['url'] = original_url if 'original_url' in locals() else item
        
    doc_ref.set(data)
    unit_str = f" {unit}" if unit else ""
    print(f"{qty}{unit_str} {item} berhasil ditambahkan ke daftar belanja!")


def get_shopping_list():
    docs = db.collection('shopping_list').where('status', '==', 'pending').stream()
    
    # Kelompokkan item berdasarkan kategori
    categorized_items = {}
    total_items = 0
    
    for doc in docs:
        data = doc.to_dict()
        unit = data.get('unit', '')
        unit_str = f" {unit}" if unit else ""
        url_str = f" (Link: {data.get('url')})" if data.get('url') else ""
        item_str = f"- {data.get('item')}: {data.get('quantity')}{unit_str}{url_str}"
        
        category = data.get('category', 'Lain-lain')
        if not category:
            category = 'Lain-lain'
            
        if category not in categorized_items:
            categorized_items[category] = []
            
        categorized_items[category].append(item_str)
        total_items += 1
    
    if total_items > 0:
        print("🛒 Daftar Belanja (belum dibeli):")
        for category, items in categorized_items.items():
            print(f"\n📂 **{category}**")
            for item in items:
                print(item)
        print(f"\nTotal: {total_items} item")
    else:
        print("Daftar belanja kosong! Tidak ada barang yang perlu dibeli.")


def _find_shopping_item_ref(item):
    # 1. Try original sanitize_id
    doc_ref = db.collection('shopping_list').document(sanitize_id(item))
    if doc_ref.get().exists:
        return doc_ref
        
    # 2. Try exact match on 'item' field
    docs = db.collection('shopping_list').where('item', '==', item).limit(1).get()
    if docs:
        return docs[0].reference
        
    # 3. Try hyphenated id as fallback
    alt_id = item.replace(' ', '-').replace('/', '-').lower()
    alt_ref = db.collection('shopping_list').document(alt_id)
    if alt_ref.get().exists:
        return alt_ref
        
    return None

def mark_as_bought(item):
    doc_ref = _find_shopping_item_ref(item)
    if doc_ref:
        doc_ref.update({
            'status': 'bought',
            'bought_at': firestore.SERVER_TIMESTAMP
        })
        print(f"✅ {item} sudah ditandai sebagai SUDAH DIBELI dan dihapus dari daftar belanja.")
    else:
        print(f"❌ {item} tidak ditemukan di daftar belanja.")


def remove_shopping_item(item):
    doc_ref = _find_shopping_item_ref(item)
    if doc_ref:
        doc_ref.delete()
        print(f"🗑️ {item} berhasil dihapus dari daftar belanja.")
    else:
        print(f"❌ {item} tidak ditemukan di daftar belanja.")


def clear_shopping_list():
    docs = db.collection('shopping_list').where('status', '==', 'bought').stream()
    batch = db.batch()
    count = 0
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
    if count > 0:
        batch.commit()
        print(f"🧹 {count} item yang sudah dibeli berhasil dibersihkan dari daftar belanja.")
    else:
        print("Tidak ada item yang perlu dibersihkan.")


def bought(item, qty, amount, category, unit=""):
    if qty < 0 or amount < 0:
        print("Error: Kuantitas dan harga tidak boleh negatif.")
        return
        
    batch = db.batch()
    
    # 1. Update shopping list
    shop_ref = _find_shopping_item_ref(item)
    if shop_ref:
        batch.set(shop_ref, {'status': 'bought', 'bought_at': firestore.SERVER_TIMESTAMP}, merge=True)
    
    # 2. Update inventory using Increment
    inv_ref = db.collection('inventory').document(sanitize_id(item))
    inv_data = {'item': item, 'updated_at': firestore.SERVER_TIMESTAMP, 'quantity': firestore.Increment(float(qty))}
    if unit: inv_data['unit'] = unit
    batch.set(inv_ref, inv_data, merge=True)
    
    # 3. Add expense
    cat = category if category else 'Belanja'
    desc = f"Beli {qty}{' '+unit if unit else ''} {item}"
    exp_ref = db.collection('expenses').document()
    batch.set(exp_ref, {
        'amount': float(amount),
        'category': cat,
        'description': desc,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    batch.commit()
    
    # 4. Potong saldo kas aset secara otomatis
    _auto_adjust_liquid_asset(-float(amount))
    
    print(f"✅ {item} dihapus dari daftar belanja (jika ada).")
    print(f"📦 Stok {item} bertambah sebanyak {qty}{' '+unit if unit else ''}.")
    print(f"💰 Pengeluaran Rp {amount:,.0f} untuk {item} berhasil dicatat.")
    
    # 5. Tampilkan Sisa Saldo Kas & Evaluasi Wants
    cash_available = get_current_cash_balance()
    print(f"💵 Sisa Cash Tersedia: Rp {cash_available:,.0f}")
    
    if is_wants_expense(cat, desc):
        month = get_current_month_str()
        start_date, end_date = get_month_bounds(month)
        docs = list(db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream())
        total_exp = sum(d.to_dict().get('amount', 0) for d in docs)
        total_wants = sum(d.to_dict().get('amount', 0) for d in docs if is_wants_expense(d.to_dict().get('category', ''), d.to_dict().get('description', '')))
        wants_pct = (total_wants / total_exp * 100) if total_exp > 0 else 0
        if wants_pct > 30:
            print(f"\n⚠️ PERINGATAN 50/30/20: Total pengeluaran 'Wants' bulan ini sudah mencapai Rp {total_wants:,.0f} ({wants_pct:.1f}% dari total pengeluaran). Melebihi batas ideal 30%!")
        else:
            print(f"\n💡 Info Wants: Porsi pengeluaran 'Wants' bulan ini berada di {wants_pct:.1f}% (Rp {total_wants:,.0f} dari total Rp {total_exp:,.0f}).")


def batch_bought(json_string):
    try:
        items = json.loads(json_string)
    except Exception as e:
        print(f"Error parse JSON: {e}")
        return
        
    batch = db.batch()
    total_amount = 0
    
    for obj in items:
        item = obj.get('item', '')
        qty = float(obj.get('qty', 1))
        amount = float(obj.get('amount', 0))
        category = obj.get('category', 'Belanja')
        unit = obj.get('unit', '')
        
        if not item: continue
        
        # 1. Update shopping list
        shop_ref = _find_shopping_item_ref(item)
        if shop_ref:
            batch.set(shop_ref, {'status': 'bought', 'bought_at': firestore.SERVER_TIMESTAMP}, merge=True)
        
        # 2. Update inventory
        inv_ref = db.collection('inventory').document(sanitize_id(item))
        inv_data = {'item': item, 'updated_at': firestore.SERVER_TIMESTAMP, 'quantity': firestore.Increment(qty)}
        if unit: inv_data['unit'] = unit
        batch.set(inv_ref, inv_data, merge=True)
        
        # 3. Add expense
        exp_ref = db.collection('expenses').document()
        batch.set(exp_ref, {
            'amount': amount,
            'category': category,
            'description': f"Beli {qty}{' '+unit if unit else ''} {item}",
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        total_amount += amount
        print(f"✅ Dicatat: {item} (Rp {amount:,.0f})")
        
    batch.commit()
    
    if total_amount > 0:
        _auto_adjust_liquid_asset(-total_amount)
        
    print(f"\n🎉 Batch transaksi selesai. Total pengeluaran: Rp {total_amount:,.0f}")
    cash_available = get_current_cash_balance()
    print(f"💵 Sisa Cash Tersedia: Rp {cash_available:,.0f}")
