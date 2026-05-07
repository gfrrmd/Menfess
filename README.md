# 💌 Menfess Bot Telegram v0.2.0

Bot Telegram untuk mengirim menfess (anonymous message) ke channel secara anonim. Dibangun dengan Python dan `python-telegram-bot` v21.

---

## ✨ Fitur

- Kirim pesan teks, foto, video, dan voice note ke channel secara anonim
- Foto & video dikirim dengan **efek spoiler** otomatis
- Pengirim mendapat **tautan langsung** ke postingan menfess
- Tombol **🗑️ Hapus Menfess** — pengirim bisa hapus menfess miliknya sendiri
- Laporan otomatis ke **Admin** setiap ada menfess masuk (nama, ID, isi, link)

---

## 🚀 Cara Deploy di Railway

### 1. Fork / Clone Repo ini
```bash
git clone https://github.com/gfrrmd/Menfess-Bot-Telegram-V.0.2.0.git
cd Menfess-Bot-Telegram-V.0.2.0
```

### 2. Buat Project Baru di Railway
1. Buka [railway.app](https://railway.app) dan login
2. Klik **New Project** → **Deploy from GitHub repo**
3. Pilih repo ini

### 3. Set Environment Variables
Di dashboard Railway, buka tab **Variables** dan tambahkan:

| Variable | Keterangan |
|----------|-----------|
| `BOT_TOKEN` | Token bot dari [@BotFather](https://t.me/BotFather) |
| `CHANNEL_ID` | ID channel tujuan (format: `-100xxxxxxxxxx`) |
| `ADMIN_ID` | Telegram User ID admin (untuk laporan menfess) |

### 4. Deploy
Railway akan otomatis build dan menjalankan bot menggunakan `Procfile`.

> ⚠️ Pastikan bot sudah dijadikan **Admin** di channel tujuan agar bisa mengirim pesan.

---

## 🤖 Cara Pakai Bot

1. Start bot dengan `/start`
2. Kirim pesan diawali `mfs!` → pesan akan diteruskan ke channel
   - Contoh: `mfs! Aku suka kamu sejak lama 😳`
3. Kamu bisa kirim **foto/video/voice** dengan caption `mfs! ...`
4. Setelah terkirim, kamu akan mendapat link dan tombol hapus

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **python-telegram-bot 21.10**
- Deploy via **Railway**

---

## 📁 Struktur File

```
├── main.py           # Logika utama bot
├── requirements.txt  # Dependensi Python
├── Procfile          # Konfigurasi proses Railway
└── README.md
```
