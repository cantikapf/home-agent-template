import os
import re

PUBLIC_DIR = r"D:\PERSONAL PROJECT\Home Agent Public"
readme_id_path = os.path.join(PUBLIC_DIR, "README.md")
readme_en_path = os.path.join(PUBLIC_DIR, "README-en.md")

# Indonesian Features
features_id = """## ✨ Fitur Lengkap

🤖 **Sistem AI & Otomatisasi**
- **Multimodal AI:** Terintegrasi dengan Gemini Vision untuk menganalisis gambar dan video.
- **Daemon Cepat:** Menggunakan Unix Socket Server (`fast_daemon.py`) agar respon AI kilat tanpa memuat ulang Python/Firebase dari awal.
- **Auto-Shopping List:** Otomatis memasukkan barang ke daftar belanja jika mendeteksi stok dapur menipis (≤ 2).
- **Laporan Otomatis:** Mengirimkan rekap keuangan mingguan secara otomatis setiap hari Minggu pukul 19:00.

💸 **Manajemen Keuangan**
- Mencatat pengeluaran harian beserta deskripsi dan kategorinya.
- Menetapkan batas *budget* bulanan.
- Mengecek sisa uang dan persentase penggunaan *budget*.
- Melihat ringkasan pengeluaran bulan ini atau bulan-bulan sebelumnya.
- **Undo/Hapus:** Membatalkan atau menghapus pengeluaran jika salah ketik.

📦 **Inventaris Kulkas & Dapur**
- Memantau stok bahan makanan (tambah/kurang) secara *real-time*.
- Cek ketersediaan semua barang di dapur dalam satu perintah.
- **Combo Cerdas:** Saat Anda melapor "sudah beli [barang]", bot otomatis melakukan 3 hal: mencoretnya dari daftar belanja, menambah stok dapur, dan mencatatnya sebagai pengeluaran.

🛒 **Daftar Belanja**
- Menambah dan menghapus barang dari daftar belanja.
- Melihat daftar barang yang berstatus *pending* (belum dibeli).
- Membersihkan keranjang dari barang yang sudah dibeli.

🍳 **Buku Resep & TikTok**
- **Ekstrak Resep TikTok:** Kirimkan URL video masakan TikTok, dan AI akan "menontonnya" untuk menyalin resep dan cara membuatnya!
- Menyimpan resep favorit ke Buku Resep *database*.
- Melihat dan membaca ulang detail resep.
- Menghapus resep yang tidak disukai.
- **AI Chef:** Meminta AI membuatkan ide masakan kreatif berdasarkan stok bahan sisa di kulkas Anda.

⏰ **Pengingat (Reminders)**
- Membuat jadwal/alarm untuk urusan rumah (contoh: "ingatkan beli token listrik besok jam 10").
- Melihat daftar pengingat yang sedang aktif/berjalan.
- Membatalkan pengingat yang tidak lagi dibutuhkan.

## 🛠️ Prasyarat (Prerequisites)"""

# English Features
features_en = """## ✨ Comprehensive Features

🤖 **AI & Automation System**
- **Multimodal AI:** Integrated with Gemini Vision to analyze images and videos.
- **Fast Daemon:** Uses a Unix Socket Server (`fast_daemon.py`) for lightning-fast AI responses without cold-starting Python/Firebase.
- **Auto-Shopping List:** Automatically adds items to your shopping list when kitchen stock runs low (≤ 2).
- **Automated Reports:** Sends a weekly financial summary automatically every Sunday at 19:00.

💸 **Financial Management**
- Record daily expenses with descriptions and categories.
- Set monthly budget limits.
- Check remaining balance and budget usage percentages.
- View expense summaries for the current or previous months.
- **Undo/Delete:** Cancel or delete an expense if you made a typo.

📦 **Fridge & Kitchen Inventory**
- Monitor grocery stocks (add/use) in *real-time*.
- Check the availability of all kitchen items in one command.
- **Smart Combo:** When you report "I bought [item]", the bot automatically does 3 things: crosses it off the shopping list, adds it to the kitchen stock, and records it as an expense.

🛒 **Shopping List**
- Add and remove items from the shopping list.
- View pending items you need to buy.
- Clear the cart of already purchased items.

🍳 **Recipe Book & TikTok**
- **TikTok Recipe Extraction:** Send a TikTok cooking video URL, and the AI will "watch" it to extract the ingredients and steps!
- Save favorite recipes to your Recipe Book database.
- View and re-read recipe details.
- Delete recipes you no longer like.
- **AI Chef:** Ask the AI to brainstorm creative cooking ideas based on leftover ingredients in your fridge.

⏰ **Reminders**
- Schedule alarms for household chores (e.g., "remind me to buy electricity tokens tomorrow at 10 AM").
- View a list of all active/pending reminders.
- Cancel reminders that are no longer needed.

## 🛠️ Prerequisites"""

# Replace in ID
with open(readme_id_path, 'r', encoding='utf-8') as f:
    content_id = f.read()
content_id = re.sub(r'## ✨ Fitur Utama.*?## 🛠️ Prasyarat \(Prerequisites\)', features_id, content_id, flags=re.DOTALL)
with open(readme_id_path, 'w', encoding='utf-8') as f:
    f.write(content_id)

# Replace in EN
with open(readme_en_path, 'r', encoding='utf-8') as f:
    content_en = f.read()
content_en = re.sub(r'## ✨ Key Features.*?## 🛠️ Prerequisites', features_en, content_en, flags=re.DOTALL)
with open(readme_en_path, 'w', encoding='utf-8') as f:
    f.write(content_en)

print("READMEs updated successfully.")
