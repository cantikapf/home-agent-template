import sys
import json
import os
import subprocess
import time

def main():
    with open('data/tiktok_recipes_found.json', 'r', encoding='utf-8') as f:
        recipes = json.load(f)
        
    progress_file = 'data/import_progress.json'
    # Start fresh or resume
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
    else:
        progress = {'processed': []}
        
    processed_urls = set(progress['processed'])
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    python_exe = sys.executable
    
    for i, item in enumerate(recipes):
        url = item['url']
        title = item['title'].encode('ascii', 'ignore').decode('ascii').lower()
        
        if url in processed_urls:
            continue
            
        print(f"\n[{i+1}/{len(recipes)}] Memproses: {item['title']}")
        
        # Skip coffee recipes
        if 'kopi' in title or 'coffee' in title or 'latte' in title or 'espresso' in title or 'mokapot' in title:
            print("[SKIP] Mengandung kata kopi. Dilewati sesuai permintaan.")
            skip_count += 1
            progress['processed'].append(url)
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f)
            continue
            
        try:
            result = subprocess.run(
                [python_exe, 'home_agent.py', '--action', 'extract_video', '--item', url],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=90
            )
            
            output = result.stdout
            err = result.stderr
            
            if result.returncode != 0:
                print(f"[ERR] Gagal menjalankan script. Error: {err.strip()}")
                fail_count += 1
            elif "Bukan video resep" in output or "tidak ditemukan" in output:
                print("[X] Gagal/Bukan Resep. Dilewati.")
                fail_count += 1
            else:
                print("[OK] Sukses disimpan ke Firestore!")
                success_count += 1
                
            progress['processed'].append(url)
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f)
                
        except subprocess.TimeoutExpired:
            print("[TIME] Timeout! Gemini terlalu lama merespons. Dilewati sementara.")
        except Exception as e:
            print(f"[ERR] Error: {e}")
            
        time.sleep(6)

    print(f"\nSelesai! Berhasil: {success_count}, Gagal: {fail_count}, Di-skip (Kopi): {skip_count}")

if __name__ == '__main__':
    main()
