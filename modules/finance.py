from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

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


def set_budget(amount, month_str=""):
    if amount < 0:
        print("Error: Budget tidak boleh negatif.")
        return
    month = month_str if month_str else get_current_month_str()
    doc_ref = db.collection('budgets').document(month)
    doc_ref.set({
        'amount': float(amount),
        'month': month,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    print(f"Budget untuk bulan {month} berhasil diatur menjadi Rp {amount:,.0f}")


def get_balance(month_str=""):
    month = month_str if month_str else get_current_month_str()
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



def _auto_adjust_liquid_asset(amount_diff):
    assets = list(db.collection('assets').stream())
    target_asset_id = 'kas'
    for doc in assets:
        data = doc.to_dict()
        if data.get('type', '').lower() in ['liquid', 'balance', 'tunai']:
            target_asset_id = doc.id
            break
            
    doc_ref = db.collection('assets').document(target_asset_id)
    doc = doc_ref.get()
    if doc.exists:
        new_amount = doc.to_dict().get('amount', 0) + float(amount_diff)
        doc_ref.update({'amount': new_amount, 'updated_at': firestore.SERVER_TIMESTAMP})
    else:
        doc_ref.set({
            'account_name': 'Kas',
            'amount': float(amount_diff),
            'type': 'Liquid',
            'updated_at': firestore.SERVER_TIMESTAMP
        })

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
    _auto_adjust_liquid_asset(-amount)
    
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

            wants_keywords = ['wants', 'keinginan', 'jajan', 'hiburan', 'hobi']
            is_wants = any(kw in category.lower() for kw in wants_keywords) or any(kw in desc.lower() for kw in wants_keywords)
            if is_wants:
                wants_budget = budget * 0.30
                # Hitung total wants
                docs_all = db.collection('expenses').where('timestamp', '>=', start_date).where('timestamp', '<', end_date).stream()
                total_wants = 0
                for d in docs_all:
                    dc = d.to_dict()
                    c = dc.get('category', '').lower()
                    ds = dc.get('description', '').lower()
                    if any(kw in c for kw in wants_keywords) or any(kw in ds for kw in wants_keywords):
                        total_wants += dc.get('amount', 0)
                
                if total_wants > wants_budget:
                    print(f"\n⚠️ PERINGATAN 50/30/20: Total pengeluaran 'Wants' (Keinginan) bulan ini (Rp {total_wants:,.0f}) sudah melebihi 30% dari total budget bulanan (Rp {wants_budget:,.0f}). Tegur pengguna untuk mengerem belanja hura-hura!")


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



def update_expense(old_name, amount, category="", desc=""):
    # Cari expense berdasarkan nama deskripsi (fuzzy/terbaru)
    docs = db.collection('expenses').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
    
    target_doc = None
    for doc in docs:
        data = doc.to_dict()
        if old_name.lower() in data.get('description', '').lower() or old_name.lower() in data.get('category', '').lower():
            target_doc = doc
            break
            
    if not target_doc:
        print(f"❌ Tidak menemukan pengeluaran dengan kata kunci '{old_name}' pada 50 transaksi terakhir.")
        return
        
    doc_ref = db.collection('expenses').document(target_doc.id)
    update_data = {}
    if amount > 0: update_data['amount'] = float(amount)
    if category: update_data['category'] = category
    if desc: update_data['description'] = desc
    
    if not update_data:
        print("⚠️ Tidak ada data yang diubah.")
        return
        
    
    old_amount = target_doc.to_dict().get('amount', 0)
    if amount > 0:
        amount_diff = old_amount - amount
        if amount_diff != 0:
            _auto_adjust_liquid_asset(amount_diff)
            
    doc_ref.update(update_data)

    print(f"✅ Pengeluaran berhasil diupdate: {target_doc.to_dict().get('description')} -> {update_data}")

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
    _auto_adjust_liquid_asset(data.get('amount', 0))
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

    # Tagihan masa depan (Bulan ini / Depan)
    current_m = now_local.strftime('%Y-%m')
    bill_docs = db.collection('scheduled_bills').where('due_month', '==', current_m).where('status', '==', 'pending').stream()
    bill_items = []
    for d in bill_docs:
        dic = d.to_dict()
        bill_items.append(f"{dic.get('item_name')} (Rp {dic.get('amount',0):,.0f})")
    
    if bill_items:
        print(f"\n🔔 TAGIHAN MENDATANG (Bulan {current_m}):")
        for b in bill_items:
            print(f"  • {b}")



def add_asset(account, amount, type_val):
    if amount < 0:
        print("Error: Amount aset tidak boleh negatif.")
        return
    doc_ref = db.collection('assets').document(sanitize_id(account))
    doc_ref.set({
        'account_name': account,
        'amount': float(amount),
        'type': type_val,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    print(f"🏦 Aset berhasil dicatat: {account} (Tipe: {type_val}) sejumlah Rp {amount:,.0f}")

def update_asset_balance(account, amount):
    doc_ref = db.collection('assets').document(sanitize_id(account))
    doc = doc_ref.get()
    if not doc.exists:
        print(f"❌ Error: Aset '{account}' tidak ditemukan. Silakan tambahkan sebagai aset baru terlebih dahulu.")
        return
        
    current_amount = doc.to_dict().get('amount', 0)
    new_amount = current_amount + float(amount)
    
    doc_ref.update({
        'amount': new_amount,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    
    action_word = "ditambahkan" if amount > 0 else "dikurangi"
    print(f"💰 Saldo aset {account} berhasil {action_word} sebesar Rp {abs(amount):,.0f}.")
    print(f"Total saldo {account} sekarang: Rp {new_amount:,.0f}")

def get_assets():
    docs = db.collection('assets').stream()
    total_liquid = 0
    total_illiquid = 0
    assets = []
    
    for doc in docs:
        data = doc.to_dict()
        amt = data.get('amount', 0)
        t = data.get('type', '').lower()
        if t in ['liquid', 'balance', 'tunai']:
            total_liquid += amt
        else:
            total_illiquid += amt
        assets.append(f"  • {data.get('account_name')} ({data.get('type')}): Rp {amt:,.0f}")
        
    print("💼 *LAPORAN TOTAL KEKAYAAN/ASET*")
    print(f"Total Aset Liquid (Cepat Cair): Rp {total_liquid:,.0f}")
    print(f"Total Aset Investasi/Deposit: Rp {total_illiquid:,.0f}")
    print(f"💰 GRAND TOTAL: Rp {(total_liquid + total_illiquid):,.0f}\\n")
    if assets:
        print("Rincian:")
        for a in assets:
            print(a)
    else:
        print("Belum ada data aset yang dicatat.")

def add_bill(item, amount, due_month, recurring=""):
    doc_ref = db.collection('scheduled_bills').document()
    data = {
        'item_name': item,
        'amount': float(amount),
        'due_month': due_month,
        'status': 'pending',
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    if recurring:
        data['recurring'] = recurring
        
    doc_ref.set(data)
    rec_str = f" (Berulang: {recurring})" if recurring else ""
    print(f"📅 Rencana tagihan '{item}' sebesar Rp {amount:,.0f} untuk bulan {due_month}{rec_str} berhasil dicatat!")

def get_bills(month_str=""):
    month = month_str if month_str else get_current_month_str()
    docs = db.collection('scheduled_bills').where('due_month', '==', month).where('status', '==', 'pending').stream()
    
    bills = []
    total = 0
    for doc in docs:
        data = doc.to_dict()
        amt = data.get('amount', 0)
        total += amt
        bills.append(f"  • [ID: {doc.id}] {data.get('item_name')}: Rp {amt:,.0f}")
        
    if bills:
        print(f"🔔 *TAGIHAN MENDATANG UNTUK BULAN {month}*")
        for b in bills:
            print(b)
        print(f"Total Estimasi Tagihan: Rp {total:,.0f}")
    else:
        print(f"✅ Tidak ada tagihan pending untuk bulan {month}.")

def get_expense_trend(category):
    if not category:
        print("Silakan tentukan kategori untuk melihat tren.")
        return
    
    now_utc = get_now_utc()
    # 3 bulan terakhir
    from datetime import timedelta
    three_months_ago = now_utc - timedelta(days=90)
    
    docs = db.collection('expenses').where('category', '==', category).where('timestamp', '>=', three_months_ago).stream()
    
    total = 0
    count = 0
    for doc in docs:
        total += doc.to_dict().get('amount', 0)
        count += 1
        
    if count == 0:
        print(f"Tidak ada data pengeluaran untuk kategori '{category}' dalam 3 bulan terakhir.")
        return
        
    avg = total / 3.0  # simple monthly average
    print(f"📈 *TREN PENGELUARAN '{category.upper()}' (3 Bulan Terakhir)*")
    print(f"Total dihabiskan: Rp {total:,.0f} (dalam {count} transaksi)")
    print(f"Rata-rata per bulan: Rp {avg:,.0f}")
