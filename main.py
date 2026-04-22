import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mengambil data dari Environment Variables Railway
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") # Contoh: -100123456789
ADMIN_ID = os.getenv("ADMIN_ID")     # ID Telegram kamu

# Database sederhana untuk fitur hapus (Hanya bertahan selama bot jalan/tidak restart)
# Untuk jangka panjang, disarankan menggunakan database asli seperti MongoDB atau PostgreSQL
menfess_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Selamat datang di Bot Menfess.\n\n"
        "Cara kirim menfess:\n"
        "Gunakan awalan **mfs!** diikuti pesan atau media kamu.\n"
        "Contoh: `mfs! Semangat ya kamu!`"
    )

async def handle_menfess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    username = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name
    
    # Cek apakah ada teks dan apakah mengandung trigger
    text_content = msg.text or msg.caption or ""
    
    if not text_content.startswith("mfs!"):
        return

    # Menghapus trigger "mfs!" dari pesan
    clean_content = text_content.replace("mfs!", "", 1).strip()
    
    try:
        # 1. Kirim ke Channel secara Anonim
        if msg.text:
            sent_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=clean_content)
        elif msg.photo:
            sent_msg = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=msg.photo[-1].file_id, caption=clean_content)
        elif msg.video:
            sent_msg = await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption=clean_content)
        elif msg.voice:
            sent_msg = await context.bot.send_voice(chat_id=CHANNEL_ID, voice=msg.voice.file_id, caption=clean_content)
        else:
            await msg.reply_text("Tipe media ini belum didukung.")
            return

        # Link pesan di channel
        channel_link = f"https://t.me/{str(CHANNEL_ID).replace('-100', '')}/{sent_msg.message_id}"
        
        # Simpan data untuk fitur hapus
        menfess_data[sent_msg.message_id] = user_id

        # 2. Notifikasi ke Pengirim dengan Tombol Hapus
        keyboard = [[InlineKeyboardButton("Hapus Menfess", callback_data=f"del_{sent_msg.message_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await msg.reply_text(
            f"✅ Menfess terkirim!\nLink: {channel_link}",
            reply_markup=reply_markup
        )

        # 3. Laporan ke Admin
        report_text = (
            f"📩 **Menfess Baru!**\n"
            f"Pengirim: {username} (`{user_id}`)\n"
            f"Link Channel: {channel_link}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=report_text)

    except Exception as e:
        await msg.reply_text(f"Gagal mengirim menfess. Pastikan ID Channel benar dan Bot sudah jadi Admin. Error: {e}")

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg_id_to_del = int(query.data.split("_")[1])
    user_id = query.from_user.id

    # Cek apakah yang klik tombol adalah yang mengirim pesan
    if menfess_data.get(msg_id_to_del) == user_id:
        try:
            await context.bot.delete_message(chat_id=CHANNEL_ID, message_id=msg_id_to_del)
            await query.answer("Menfess berhasil dihapus!")
            await query.edit_message_text("Menfess telah dihapus dari channel.")
        except:
            await query.answer("Gagal menghapus pesan. Mungkin pesan sudah dihapus sebelumnya.", show_alert=True)
    else:
        await query.answer("Kamu tidak punya akses untuk menghapus menfess ini!", show_alert=True)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_menfess))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^del_"))
    
    print("Bot is running...")
    app.run_polling()
