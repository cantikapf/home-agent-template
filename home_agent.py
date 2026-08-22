import sys
import argparse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import tempfile
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone
import dateutil.parser # type: ignore

# Inisialisasi Firebase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

def get_current_month_str():
    return get_now_utc().astimezone().strftime('%Y-%m')

def get_month_bounds(month_str):
    """Return start and end datetimes (UTC aware) for the given month string YYYY-MM."""
    dt_local = datetime.strptime(month_str + '-01', '%Y-%m-%d')
    start_date = dt_local.replace(tzinfo=datetime.now().astimezone().tzinfo).astimezone(timezone.utc)
    
    if dt_local.month == 12:
        next_month_local = datetime(dt_local.year + 1, 1, 1)
    else:
        next_month_local = datetime(dt_local.year, dt_local.month + 1, 1)
        
    end_date = next_month_local.replace(tzinfo=datetime.now().astimezone().tzinfo).astimezone(timezone.utc)
    return start_date, end_date

def set_budget(amount):
    if amount < 0:
        print("Error: Budget tidak boleh negatif.")
        return
    month = get_current_month_str()
    doc_ref = db.collection('budgets').document(month)
    doc_ref.set({
        'amount': float(amount),
        'month': month,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    print(f"Budget untuk bulan {month} berhasil diatur menjadi Rp {amount:,.0f}")

def get_balance():
    month = get_current_month_str()
    budget_doc = db.collection('budgets').document(month).get()
    budget = budget_doc.to_dict().get('amount', 0) if budget_doc.exists else 0
        
    start_date, end_date = get_month_bounds(month)
    docs = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
    
    total_expense = sum(d.to_dict().get('amount', 0) for d in docs)
    balance = budget - total_expense
    
    print(f"Laporan Keuangan Bulan {month}:")
    print(f"Batas Budget: Rp {budget:,.0f}")
    print(f"Total Pengeluaran: Rp {total_expense:,.0f}")
    print(f"Sisa Uang/Budget: Rp {balance:,.0f}")
    
    if budget > 0:
        percent = (total_expense / budget) * 100
        if percent >= 100:
            print("PERINGATAN BUDGET: Pengeluaran Anda sudah MELEBIHI budget bulan ini! Tolong nasihati pengguna dengan tegas.")
        elif percent >= 80:
            print(f"PERINGATAN BUDGET: Pengeluaran Anda sudah mencapai {percent:.1f}% dari budget! Tolong ingatkan pengguna untuk berhemat.")

def add_expense(amount, category, desc):
    if amount < 0:
        print("Error: Pengeluaran tidak boleh negatif.")
        return
    doc_ref = db.collection('expenses').document()
    doc_ref.set({
        'amount': float(amount),
        'category': category,
        'description': desc,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    print(f"Pengeluaran sebesar Rp {amount:,.0f} untuk {category} ({desc}) berhasil dicatat di Firebase!")
    
    # Check budget
    month = get_current_month_str()
    budget_doc = db.collection('budgets').document(month).get()
    if budget_doc.exists:
        budget = budget_doc.to_dict().get('amount', 0)
        start_date, end_date = get_month_bounds(month)
        docs = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
        total_expense = sum(d.to_dict().get('amount', 0) for d in docs)
        
        if budget > 0:
            percent = (total_expense / budget) * 100
            if percent >= 100:
                print("PERINGATAN BUDGET KERAS: Pembelian ini membuat Anda MELEBIHI budget bulan ini! Marahi pengguna agar berhenti belanja!")
            elif percent >= 90:
                print("PERINGATAN BUDGET KERAS: Pembelian ini membuat sisa budget bulan ini hampir habis (Tersisa < 10%). Tolong beri peringatan tegas!")

def add_shopping_list(item, qty, unit=""):
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
            response = urllib.request.urlopen(req)
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
                        item = "Barang dari Link"
                        
            # Tambahkan penanda platform untuk kejelasan daftar belanja
            if 'shopee' in final_url.lower() and '(Shopee)' not in item:
                item += " (Shopee)"
            elif 'tokopedia' in final_url.lower() and '(Tokopedia)' not in item:
                item += " (Tokopedia)"
        except Exception as e:
            print(f"Gagal mengekstrak link: {e}")
            item = "Barang dari Link"

    doc_ref = db.collection('shopping_list').document(sanitize_id(item))
    data = {'item': item, 'quantity': qty, 'status': 'pending'}
    if unit: data['unit'] = unit
    if 'http' in str(item) or 'Barang dari Link' in item or '(Shopee)' in item or '(Tokopedia)' in item:
        # Jika berhasil di ekstrak, simpan url aslinya
        data['url'] = original_url if 'original_url' in locals() else item
        
    doc_ref.set(data)
    unit_str = f" {unit}" if unit else ""
    print(f"{qty}{unit_str} {item} berhasil ditambahkan ke daftar belanja!")

def get_shopping_list():
    docs = db.collection('shopping_list').where('status', '==', 'pending').stream()
    items = []
    for doc in docs:
        data = doc.to_dict()
        unit = data.get('unit', '')
        unit_str = f" {unit}" if unit else ""
        url_str = f" (Link: {data.get('url')})" if data.get('url') else ""
        items.append(f"- {data.get('item')}: {data.get('quantity')}{unit_str}{url_str}")
    
    if items:
        print("🛒 Daftar Belanja (belum dibeli):")
        for item in items:
            print(item)
        print(f"\nTotal: {len(items)} item")
    else:
        print("Daftar belanja kosong! Tidak ada barang yang perlu dibeli.")

def mark_as_bought(item):
    doc_ref = db.collection('shopping_list').document(sanitize_id(item))
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            'status': 'bought',
            'bought_at': firestore.SERVER_TIMESTAMP
        })
        print(f"✅ {item} sudah ditandai sebagai SUDAH DIBELI dan dihapus dari daftar belanja.")
    else:
        print(f"❌ {item} tidak ditemukan di daftar belanja.")

def remove_shopping_item(item):
    doc_ref = db.collection('shopping_list').document(sanitize_id(item))
    doc = doc_ref.get()
    if doc.exists:
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
    shop_ref = db.collection('shopping_list').document(sanitize_id(item))
    shop_doc = shop_ref.get()
    if shop_doc.exists:
        batch.update(shop_ref, {'status': 'bought', 'bought_at': firestore.SERVER_TIMESTAMP})
    
    # 2. Update inventory using Increment
    inv_ref = db.collection('inventory').document(sanitize_id(item))
    inv_data = {'item': item, 'updated_at': firestore.SERVER_TIMESTAMP, 'quantity': firestore.Increment(float(qty))}
    if unit: inv_data['unit'] = unit
    batch.set(inv_ref, inv_data, merge=True)
    
    # 3. Add expense
    exp_ref = db.collection('expenses').document()
    batch.set(exp_ref, {
        'amount': float(amount),
        'category': category if category else 'Belanja',
        'description': f"Beli {qty}{' '+unit if unit else ''} {item}",
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    batch.commit()
    print(f"✅ {item} dihapus dari daftar belanja (jika ada).")
    print(f"📦 Stok {item} bertambah sebanyak {qty}{' '+unit if unit else ''}.")
    print(f"💰 Pengeluaran Rp {amount:,.0f} untuk {item} berhasil dicatat.")
    
    # 4. Check budget
    month = get_current_month_str()
    budget_doc = db.collection('budgets').document(month).get()
    if budget_doc.exists:
        budget = budget_doc.to_dict().get('amount', 0)
        start_date, end_date = get_month_bounds(month)
        docs = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
        total_expense = sum(d.to_dict().get('amount', 0) for d in docs)
        if budget > 0:
            percent = (total_expense / budget) * 100
            balance = budget - total_expense
            print(f"📊 Sisa budget bulan ini: Rp {balance:,.0f} ({100-percent:.1f}% tersisa)")
            if percent >= 100:
                print("🚨 PERINGATAN: Budget bulan ini sudah MELEBIHI BATAS!")
            elif percent >= 80:
                print("⚠️ PERINGATAN: Budget bulan ini hampir habis!")

def update_inventory(item, qty, action, unit=""):
    if qty < 0:
        print("Error: Kuantitas tidak boleh negatif.")
        return
        
    doc_ref = db.collection('inventory').document(sanitize_id(item))
    
    inc_val = float(qty) if action == 'add' else -float(qty)
    data = {'item': item, 'updated_at': firestore.SERVER_TIMESTAMP, 'quantity': firestore.Increment(inc_val)}
    if unit: data['unit'] = unit
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
            shop_ref.set({'item': item, 'quantity': 1, 'unit': final_unit, 'status': 'pending'})
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

def get_expenses():
    docs = db.collection('expenses').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
    result = "10 Pengeluaran Terakhir:\n"
    total = 0
    for doc in docs:
        data = doc.to_dict()
        amount = data.get('amount', 0)
        total += amount
        # Coba ambil timestamp, jika tidak ada fallback
        ts = data.get('timestamp')
        date_str = ""
        if ts:
            date_str = ts.astimezone().strftime('%d/%m %H:%M') + " - "
        result += f"- [ID: {doc.id}] {date_str}{data.get('category')}: Rp {amount:,.0f} ({data.get('description')})\n"
    print(result if total > 0 else "Belum ada catatan pengeluaran.")

def delete_expense(doc_id):
    if not doc_id or doc_id.lower() == 'last':
        # Cari yang paling terakhir
        docs = list(db.collection('expenses').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream())
        if not docs:
            print("Tidak ada pengeluaran yang bisa dihapus.")
            return
        doc_id = docs[0].id
        data = docs[0].to_dict()
    else:
        doc = db.collection('expenses').document(doc_id).get()
        if not doc.exists:
            print(f"Pengeluaran dengan ID {doc_id} tidak ditemukan.")
            return
        data = doc.to_dict()

    db.collection('expenses').document(doc_id).delete()
    print(f"🗑️ Pengeluaran berhasil dihapus: {data.get('category')} - Rp {data.get('amount', 0):,.0f} ({data.get('description')})")


def get_expense_summary(month_str=""):
    month = month_str if month_str else get_current_month_str()
    try:
        start_date, end_date = get_month_bounds(month)
    except Exception as e:
        print(f"Format bulan salah. Gunakan YYYY-MM. Error: {e}")
        return
    
    docs = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
    
    categories = {}
    total = 0
    count = 0
    for doc in docs:
        data = doc.to_dict()
        cat = data.get('category', 'Lain-lain')
        amount = data.get('amount', 0)
        categories[cat] = categories.get(cat, 0) + amount
        total += amount
        count += 1
    
    if not categories:
        print("Belum ada pengeluaran bulan ini.")
        return
    
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    
    print(f"📊 Ringkasan Pengeluaran Bulan {month}:")
    print(f"Total: Rp {total:,.0f} ({count} transaksi)\n")
    print("Per Kategori:")
    for cat, amount in sorted_cats:
        percent = (amount / total) * 100 if total > 0 else 0
        bar = "█" * int(percent / 5)
        print(f"  {cat}: Rp {amount:,.0f} ({percent:.1f}%) {bar}")
    
    budget_doc = db.collection('budgets').document(month).get()
    if budget_doc.exists:
        budget = budget_doc.to_dict().get('amount', 0)
        if budget > 0:
            balance = budget - total
            percent_used = (total / budget) * 100
            print(f"\n💰 Budget: Rp {budget:,.0f}")
            print(f"💸 Terpakai: Rp {total:,.0f} ({percent_used:.1f}%)")
            print(f"💵 Sisa: Rp {balance:,.0f}")

def get_weekly_report():
    from datetime import timedelta
    now_utc = get_now_utc()
    week_ago_utc = now_utc - timedelta(days=7)
    
    # Pengeluaran minggu ini
    docs = db.collection('expenses').where('timestamp', '>=', week_ago_utc).where('timestamp', '<', now_utc).stream()
    categories = {}
    total = 0
    for doc in docs:
        data = doc.to_dict()
        cat = data.get('category', 'Lain-lain')
        amount = data.get('amount', 0)
        categories[cat] = categories.get(cat, 0) + amount
        total += amount
    
    print("📋 *LAPORAN MINGGUAN RUMAH TANGGA*\n")
    # Tampilkan tanggal dalam lokal WIB untuk laporan
    now_local = now_utc.astimezone()
    week_ago_local = week_ago_utc.astimezone()
    print(f"Periode: {week_ago_local.strftime('%d/%m')} - {now_local.strftime('%d/%m/%Y')}\n")
    
    if total > 0:
        print(f"💸 Total pengeluaran minggu ini: Rp {total:,.0f}")
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        for cat, amount in sorted_cats:
            print(f"  • {cat}: Rp {amount:,.0f}")
    else:
        print("💸 Tidak ada pengeluaran minggu ini.")
    
    # Budget info
    month = now_local.strftime('%Y-%m')
    budget_doc = db.collection('budgets').document(month).get()
    if budget_doc.exists:
        budget = budget_doc.to_dict().get('amount', 0)
        if budget > 0:
            start_date, end_date = get_month_bounds(month)
            month_docs = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
            month_total = sum(d.to_dict().get('amount', 0) for d in month_docs)
            balance = budget - month_total
            print(f"\n💰 Sisa budget bulan ini: Rp {balance:,.0f}")
    
    # Stok hampir habis
    inv_docs = db.collection('inventory').stream()
    low_items = []
    for doc in inv_docs:
        data = doc.to_dict()
        qty = data.get('quantity', 0)
        if qty <= 2:
            unit = data.get('unit', '')
            unit_str = f" {unit}" if unit else ""
            status = "HABIS" if qty <= 0 else f"sisa {qty}{unit_str}"
            low_items.append(f"  • {data.get('item')} ({status})")
    
    if low_items:
        print(f"\n⚠️ Stok perlu dibeli ({len(low_items)} item):")
        for item in low_items:
            print(item)
    
    # Daftar belanja pending
    shop_docs = db.collection('shopping_list').where('status', '==', 'pending').stream()
    shop_items = [doc.to_dict().get('item', '') for doc in shop_docs]
    if shop_items:
        print(f"\n🛒 Belum dibeli ({len(shop_items)} item): {', '.join(shop_items)}")

def generate_recipe(ingredients):
    print(f"Tolong buatkan resep masakan rumahan kreatif menggunakan bahan-bahan berikut: {ingredients}")

def add_reminder(task, time_str):
    try:
        # User inputs local time string. Parse and convert to UTC.
        dt_local = dateutil.parser.parse(time_str)
        if dt_local.tzinfo is None:
            dt_local = dt_local.replace(tzinfo=datetime.now().astimezone().tzinfo)
        dt_utc = dt_local.astimezone(timezone.utc)
        
        doc_ref = db.collection('reminders').document()
        doc_ref.set({
            'task': task,
            'time_str': dt_local.strftime('%Y-%m-%d %H:%M'),
            'timestamp': dt_utc,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        })
        print(f"Pengingat berhasil disimpan: '{task}' pada waktu {dt_local.strftime('%d-%m-%Y %H:%M')}.")
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

def save_recipe(name, ingredients, steps, source_url=""):
    doc_ref = db.collection('recipes').document()
    doc_ref.set({
        'name': name,
        'ingredients': ingredients,
        'steps': steps,
        'source_url': source_url,
        'created_at': firestore.SERVER_TIMESTAMP
    })
    print(f"✅ Resep '{name}' berhasil disimpan ke database!")

def extract_video_recipe(url):
    from google import genai
    import subprocess
    try:
        is_tiktok = 'tiktok.com' in url
        is_youtube = 'youtube.com' in url or 'youtu.be' in url
        
        if not (is_tiktok or is_youtube):
            print("❌ URL tidak valid. Hanya menerima tautan TikTok atau YouTube.")
            return

        print(f"Sedang memproses video dari {'TikTok' if is_tiktok else 'YouTube'}... (mohon tunggu beberapa saat)")
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            env_path = os.path.join(BASE_DIR, '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.strip().split('=', 1)[1]
                            break
                            
        if not api_key:
            print("❌ GEMINI_API_KEY tidak ditemukan.")
            return
            
        client = genai.Client(api_key=api_key)
        
        if is_youtube:
            from google.genai import types
            # YouTube dapat diproses secara native oleh Gemini menggunakan Part.from_uri
            video_part = types.Part.from_uri(file_uri=url, mime_type='video/mp4')
            prompt = "Tolong tonton video YouTube ini dan ekstrak resep masakannya secara detail dan akurat. Format output yang wajib: 1. Nama Masakan, 2. Bahan-bahan, 3. Cara Membuat. Jika sama sekali bukan video resep, katakan saja 'Bukan video resep'."
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[video_part, prompt]
            )
            print("\n--- HASIL EKSTRAKSI YOUTUBE (GEMINI AI) ---")
            print(ai_response.text)
            print("------------------------------------------------\n")
            print(f"💡 Instruksi untuk AI: Tampilkan hasil ekstraksi AI di atas kepada pengguna persis seperti itu (sebagai draf). Jika pengguna bilang oke, simpan menggunakan action `save_recipe` dengan URL {url}.")
            return
            
        # Jika TikTok, kita download dulu videonya
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            video_path = tmp_file.name

        title = "Tanpa Judul"
        api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('code') != 0:
            print(f"❌ Gagal mendapatkan data dari TikTok: {data.get('msg')}")
            os.remove(video_path)
            return
            
        play_url = data.get('data', {}).get('play')
        title = data.get('data', {}).get('title', 'Tanpa Judul')
        urllib.request.urlretrieve(play_url, video_path)
        
        video_file = client.files.upload(file=video_path)
        
        while video_file.state.name == 'PROCESSING':
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == 'FAILED':
            print("❌ Pemrosesan video TikTok oleh AI gagal.")
            os.remove(video_path)
            return
            
        prompt = f"Video TikTok ini berjudul '{title}'. Tolong tonton videonya, baca teks yang muncul di layar, dan dengarkan suaranya. Ekstrak resep masakan dari video ini! Format output yang wajib: 1. Nama Masakan, 2. Bahan-bahan, 3. Cara Membuat. Jika video ini sama sekali bukan tentang resep/masakan, katakan saja 'Bukan video resep'."
        
        ai_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[video_file, prompt]
        )
        
        print("\n--- HASIL EKSTRAKSI TIKTOK (GEMINI AI VIDEO) ---")
        print(ai_response.text)
        print("------------------------------------------------\n")
        print(f"💡 Instruksi untuk AI: Tampilkan hasil ekstraksi AI di atas kepada pengguna persis seperti itu (sebagai draf). Jika pengguna bilang oke, simpan menggunakan action `save_recipe` dengan URL {url}.")
        
        try:
            client.files.delete(name=video_file.name)
            os.remove(video_path)
        except:
            pass
            
    except Exception as e:
        print(f"SYSTEM_ERROR: Terjadi kesalahan sistem saat memproses video: {e}")

def get_recipes():
    docs = db.collection('recipes').stream()
    recipes = []
    for doc in docs:
        data = doc.to_dict()
        recipes.append(f"- **{data.get('name', 'Tanpa Nama')}**\n  Bahan: {data.get('ingredients', '')}")
    
    if recipes:
        print("📖 BUKU RESEP SAYA:")
        for r in recipes:
            print(r)
    else:
        print("Buku resep masih kosong.")

def read_recipe(name):
    docs = db.collection('recipes').stream()
    found = False
    for doc in docs:
        data = doc.to_dict()
        recipe_name = data.get('name', '')
        if name.lower() in recipe_name.lower():
            print(f"\n🍳 RESEP: {recipe_name}")
            print(f"🔗 Sumber: {data.get('source_url', '-')}")
            print("\n🛒 Bahan-bahan:")
            print(data.get('ingredients', ''))
            print("\n👨‍🍳 Cara Membuat:")
            print(data.get('steps', ''))
            found = True
            break
            
    if not found:
        print(f"❌ Resep dengan nama '{name}' tidak ditemukan di Buku Resep.")

def delete_recipe(name):
    docs = db.collection('recipes').stream()
    deleted = False
    for doc in docs:
        data = doc.to_dict()
        if name.lower() in data.get('name', '').lower():
            doc.reference.delete()
            print(f"🗑️ Resep '{data.get('name')}' berhasil dihapus.")
            deleted = True
            break
    if not deleted:
        print(f"❌ Resep dengan nama '{name}' tidak ditemukan untuk dihapus.")

def main():
    parser = argparse.ArgumentParser(description="Home Agent CLI")
    parser.add_argument('--action', required=True, choices=[
        'expense', 'shopping', 'inventory', 'recipe', 'get_inventory', 'get_expenses', 
        'set_budget', 'get_balance', 'add_reminder', 'get_reminders', 'delete_reminder',
        'get_shopping_list', 'mark_bought', 'remove_shopping', 'clear_bought',
        'bought', 'get_expense_summary', 'weekly_report', 'delete_expense',
        'save_recipe', 'extract_video', 'get_recipes', 'read_recipe', 'delete_recipe'
    ])
    parser.add_argument('--doc_id', type=str, default="")
    parser.add_argument('--month', type=str, default="")
    parser.add_argument('--amount', type=float, default=0)
    parser.add_argument('--category', type=str, default="")
    parser.add_argument('--desc', type=str, default="")
    parser.add_argument('--item', type=str, default="")
    parser.add_argument('--qty', type=float, default=1)
    parser.add_argument('--unit', type=str, default="")
    parser.add_argument('--inv_action', choices=['add', 'use'], default='add')
    parser.add_argument('--ingredients', type=str, default="")
    parser.add_argument('--task', type=str, default="")
    parser.add_argument('--time', type=str, default="")
    parser.add_argument('--name', type=str, default="")
    parser.add_argument('--steps', type=str, default="")
    parser.add_argument('--url', type=str, default="")

    args = parser.parse_args()

    if args.action == 'expense': add_expense(args.amount, args.category, args.desc)
    elif args.action == 'delete_expense': delete_expense(args.doc_id)
    elif args.action == 'get_reminders': get_reminders()
    elif args.action == 'delete_reminder': delete_reminder(args.task)
    elif args.action == 'delete_recipe': delete_recipe(args.name)
    elif args.action == 'shopping': add_shopping_list(args.item, args.qty, args.unit)
    elif args.action == 'inventory': update_inventory(args.item, args.qty, args.inv_action, args.unit)
    elif args.action == 'recipe': generate_recipe(args.ingredients)
    elif args.action == 'get_inventory': get_inventory()
    elif args.action == 'get_expenses': get_expenses()
    elif args.action == 'set_budget': set_budget(args.amount)
    elif args.action == 'get_balance': get_balance()
    elif args.action == 'add_reminder': add_reminder(args.task, args.time)
    elif args.action == 'get_shopping_list': get_shopping_list()
    elif args.action == 'mark_bought': mark_as_bought(args.item)
    elif args.action == 'remove_shopping': remove_shopping_item(args.item)
    elif args.action == 'clear_bought': clear_shopping_list()
    elif args.action == 'bought': bought(args.item, args.qty, args.amount, args.category, args.unit)
    elif args.action == 'get_expense_summary': get_expense_summary(args.month)
    elif args.action == 'weekly_report': get_weekly_report()
    elif args.action == 'save_recipe': save_recipe(args.name, args.ingredients, args.steps, args.url)
    elif args.action == 'extract_video': extract_video_recipe(args.url)
    elif args.action == 'get_recipes': get_recipes()
    elif args.action == 'read_recipe': read_recipe(args.name)

if __name__ == '__main__':
    main()
