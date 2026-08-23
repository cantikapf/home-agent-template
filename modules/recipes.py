from firebase_admin import firestore
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import dateutil.parser
import uuid
from .db import db, get_now_utc, sanitize_id

import json
import tempfile
import subprocess
import os
def generate_recipe(ingredients):
    print(f"Tolong buatkan resep masakan rumahan kreatif menggunakan bahan-bahan berikut: {ingredients}")


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
            env_path = os.path.expanduser('~/.hermes/.env')
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
        
        # Timeout setelah 120 detik (60 iterasi x 2 detik)
        max_wait = 60
        wait_count = 0
        while video_file.state.name == 'PROCESSING':
            time.sleep(2)
            wait_count += 1
            if wait_count >= max_wait:
                print("❌ Timeout: Pemrosesan video terlalu lama (>2 menit). Coba lagi nanti.")
                os.remove(video_path)
                return
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

