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

