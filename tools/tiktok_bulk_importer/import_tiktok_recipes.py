import json
import os
import subprocess
import time
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Import recipes from JSON to Home Agent.')
    parser.add_argument('--input', type=str, default='tiktok_recipes_found.json', help='Path to recipes JSON')
    parser.add_argument('--python-cmd', type=str, default='python', help='Python command (e.g., python3 or venv/Scripts/python)')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.input} tidak ditemukan. Jalankan scan_tiktok_recipes.py terlebih dahulu.")
        sys.exit(1)
        
    progress_file = 'import_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
    else:
        progress = {'processed': []}
        
    processed_urls = set(progress['processed'])
    print(f"Total resep: {len(recipes)}. Sudah diproses: {len(processed_urls)}")
    
    # Path to home_agent.py (assuming it's two levels up)
    home_agent_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'home_agent.py'))
    
    if not os.path.exists(home_agent_script):
        print(f"Error: home_agent.py tidak ditemukan di {home_agent_script}")
        sys.exit(1)
    
    success_count = 0
    fail_count = 0
    
    for i, item in enumerate(recipes):
        url = item['url']
        title = item['title'].encode('ascii', 'ignore').decode('ascii')
        
        if url in processed_urls:
            continue
            
        print(f"\n[{i+1}/{len(recipes)}] Memproses: {title}")
        print(f"URL: {url}")
        
        # Rewrite tiktokv.com to standard tiktok.com
        if 'tiktokv.com' in url:
            video_id = url.rstrip('/').split('/')[-1]
            url = f"https://www.tiktok.com/video/{video_id}"

        try:
            # PENTING: Gunakan PYTHONIOENCODING=utf-8 agar print emoji tidak crash di Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                [args.python_cmd, home_agent_script, '--action', 'extract_video', '--item', url],
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env,
                timeout=90
            )
            
            output = result.stdout
            err = result.stderr
            
            if result.returncode != 0 or "SYSTEM_ERROR" in output:
                print(f"[ERR] Gagal menjalankan script. Error: {output.strip()} {err.strip()}")
                fail_count += 1
            elif "Bukan video resep" in output or "tidak ditemukan" in output or "❌" in output:
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
            
        # Jeda untuk menghindari Rate Limit
        time.sleep(6)

    print(f"\nSelesai! Berhasil ditambahkan: {success_count}, Gagal/Bukan Resep: {fail_count}")

if __name__ == '__main__':
    main()
