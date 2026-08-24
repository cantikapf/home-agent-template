---
name: server_vps
description: Panduan untuk mengecek status server VPS
---

# Instructions
Anda dapat mengecek status server VPS pengguna melalui terminal Linux (Ubuntu).
Jalankan perintah ini secara langsung menggunakan tool terminal/command execution yang Anda miliki.

## 1. Cek Koneksi Jaringan (Ping)
Gunakan perintah ini untuk memastikan server dapat dijangkau:
ping -c 4 <IP_ADDRESS_ATAU_DOMAIN>
*(Ganti <IP_ADDRESS_ATAU_DOMAIN> dengan IP server pengguna. Jika pengguna belum menyebutkan IP-nya, gunakan 127.0.0.1 untuk mengecek VPS ini sendiri, atau tanyakan kepada pengguna).*

## 2. Cek Status Web Server (HTTP/HTTPS)
Jika pengguna memiliki website, Anda bisa mengecek status kode HTTP-nya:
curl -Is http://<IP_ADDRESS_ATAU_DOMAIN> | head -n 1

## 3. Cek Port Spesifik (misal: SSH/22)
Gunakan netcat (nc) untuk mengecek apakah port tertentu terbuka di Ubuntu:
nc -zv <IP_ADDRESS_ATAU_DOMAIN> <PORT_NUMBER>
*(Port contoh: 22 untuk SSH, 80 untuk HTTP, 443 untuk HTTPS).*

## 4. Cek Penggunaan RAM dan CPU Server Ini Sendiri (Local VPS)
Jika pengguna bertanya "bagaimana kondisi server?", jalankan perintah berikut:
- Cek RAM: free -h
- Cek CPU/Load: uptime
- Cek Disk: df -h /

**Catatan untuk AI:**
Selalu infokan hasilnya dengan bahasa yang ramah layaknya asisten rumah tangga.
Misalnya: "Tuan, saya sudah mengecek servernya. Semuanya berjalan lancar! Koneksi stabil." atau "Wah, sepertinya server sedang tidak bisa dihubungi, Tuan."
