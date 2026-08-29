#!/usr/bin/env python3
"""
Home Agent - Firestore Database Cold Backup Script
Mengekspor seluruh koleksi Firestore ke format JSON terstruktur di laptop lokal.
Bisa dijalankan langsung dari lokal tanpa memerlukan VPS aktif.
"""

import os
import sys
import json
import gzip
from datetime import datetime, timezone, date
from pathlib import Path

# Pastikan import modules.db berhasil
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Pastikan output konsol mendukung UTF-8 di Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from modules.db import db
except ImportError as e:
    print(f"Error mengimpor modules.db: {e}")
    sys.exit(1)

BACKUP_DIR = PROJECT_ROOT / "backups" / "firestore_dumps"
RETENTION_COUNT = 30  # Simpan 30 snapshot harian terakhir

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def run_backup():
    print("=" * 60)
    print("📦 Home Agent - Memulai Cold Backup Database Firestore")
    print("=" * 60)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file_json = BACKUP_DIR / f"firestore_backup_{timestamp}.json"
    backup_file_gz = BACKUP_DIR / f"firestore_backup_{timestamp}.json.gz"
    latest_file = BACKUP_DIR / "firestore_backup_latest.json"

    # Daftar koleksi utama
    core_collections = ['expenses', 'inventory', 'shopping_list', 'recipes', 'assets', 'bills']
    
    # Ambil semua koleksi (termasuk koleksi dinamis jika ada)
    try:
        discovered_collections = [col.id for col in db.collections()]
        all_collections = sorted(list(set(core_collections + discovered_collections)))
    except Exception as e:
        print(f"⚠️ Gagal mendiscover koleksi dinamis ({e}), menggunakan daftar default.")
        all_collections = core_collections

    print(f"🔍 Koleksi yang akan di-backup ({len(all_collections)}): {', '.join(all_collections)}")

    dump_data = {
        "_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": getattr(db, 'project', os.environ.get('GCP_PROJECT_ID', 'home-agent-prod')),
            "collection_count": len(all_collections)
        },
        "collections": {}
    }

    total_docs = 0

    for col_name in all_collections:
        try:
            col_ref = db.collection(col_name)
            docs = col_ref.stream()
            col_docs = []
            for doc in docs:
                data = doc.to_dict() or {}
                data['_id'] = doc.id
                col_docs.append(data)
            
            dump_data["collections"][col_name] = col_docs
            total_docs += len(col_docs)
            print(f"  • [{col_name}]: {len(col_docs)} dokumen berhasil diekspor")
        except Exception as e:
            print(f"  ❌ Gagal mengekspor koleksi {col_name}: {e}")
            dump_data["collections"][col_name] = []

    # 1. Simpan versi JSON standar
    with open(backup_file_json, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, ensure_ascii=False, indent=2, default=json_serial)

    # 2. Simpan versi GZIP terkompresi
    with gzip.open(backup_file_gz, "wt", encoding="utf-8") as f:
        json.dump(dump_data, f, ensure_ascii=False, default=json_serial)

    # 3. Update pointer 'latest'
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, ensure_ascii=False, indent=2, default=json_serial)

    json_size_kb = round(os.path.getsize(backup_file_json) / 1024, 2)
    gz_size_kb = round(os.path.getsize(backup_file_gz) / 1024, 2)

    print("-" * 60)
    print(f"✅ Backup Selesai! Total dokumen: {total_docs}")
    print(f"   📄 JSON: {backup_file_json.name} ({json_size_kb} KB)")
    print(f"   🗜️ GZIP: {backup_file_gz.name} ({gz_size_kb} KB)")
    print(f"   🔗 Latest: {latest_file.name}")

    # 4. Rotasi Backup (Hapus backup lebih tua dari RETENTION_COUNT)
    existing_backups = sorted(
        BACKUP_DIR.glob("firestore_backup_*.json"),
        key=os.path.getctime,
        reverse=True
    )
    if len(existing_backups) > RETENTION_COUNT:
        print(f"🧹 Membersihkan backup lama (Maks {RETENTION_COUNT} snapshot)...")
        for old in existing_backups[RETENTION_COUNT:]:
            old.unlink(missing_ok=True)
            # Hapus juga versi gz-nya jika ada
            gz_partner = old.with_suffix(".json.gz")
            gz_partner.unlink(missing_ok=True)
            print(f"  🗑️ Dihapus: {old.name}")

    print("=" * 60)

if __name__ == "__main__":
    run_backup()
