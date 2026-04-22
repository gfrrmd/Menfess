import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- SETUP LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# --- CONFIGURATION (RAILWAY VARIABLES) ---
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

# Database sementara untuk fitur hapus (Hilang jika bot restart)
menfess_data = {}

# --- FUNGSI START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Selamat datang di Bot Menfess Gaydar!\n\n"
        "Kirim pesan dengan awalan mfs! agar pesanmu terkirim ke channel. "
        "Kamu juga bisa mengirim Foto, Video, dan media lainnya. "
        "Pastikan menggunakan awalan mfs!"
    )

# --- FUNGSI HANDLE MENFESS ---
async def handle_menfess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    
    user_id = msg.from_user.id
    # Nama pengirim untuk laporan ke admin
    sender_name = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name
    
    # Ambil teks/caption
    text_content = msg.text or msg.caption or ""
    
    # Cek trigger
    if not text_content.startswith("mfs!"):
        return

    # Ubah trigger mfs! menjadi 💌
    clean_content = text_content.replace("mfs!", "💌", 1).strip()
    
    try:
        sent_msg = None
        
        # 1. Kirim ke Channel dengan Logika Media
        if msg.text:
            sent_msg = await context.bot.send_message(
                chat_id=CHANNEL_ID, 
                text=clean_content
            )
        elif msg.photo:
            sent_msg = await context.bot.send_photo(
                chat_id=CHANNEL_ID, 
                photo=msg.photo[-1].file_id, 
                caption=clean_content,
                has_spoiler=True # Efek Spoiler
            )
        elif msg.video:
            sent_msg = await context.bot.send_video(
                chat_id=CHANNEL_ID, 
                video=msg.video.file_id, 
                caption=clean_content,
                has_spoiler=True # Efek Spoiler
            )
        elif msg.voice:
            sent_msg = await context.bot.send_voice(
                chat_id=CHANNEL_ID, 
                voice=msg.voice.file_id, 
                caption=clean_content
            )
        else:
            await msg.reply_text("Tipe media ini belum didukung.")
            return

        # 2. Buat Tautan Channel
        clean_ch_id = str(CHANNEL_ID).replace("-100", "")
        channel_link = f"https://t.me/c/{clean_ch_id}/{sent_msg.message_id}"
        
        # Simpan relasi pesan untuk fitur hapus
        menfess_data[sent_msg.message_id] = user_id

        # 3. Notifikasi Balasan ke Pengirim
        keyboard = [[InlineKeyboardButton("🗑️ Hapus Menfess", callback_data=f"del_{sent_msg.message_id}")]]
        await msg.reply_text(
            f"✅ **Menfess terkirim!**\n\nBerikut tautan menfess kamu:\n{channel_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        # 4. Info Pengirim ke Admin
        admin_report = (
            f"📩 **LAPORAN MENFESS**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 **Pengirim:** {sender_name}\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"🔗 **Link:** [Lihat Pesan]({channel_link})\n"
            f"💬 **Isi:** {clean_content}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID, 
            text=admin_report, 
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Gagal kirim menfess: {e}")
        await msg.reply_text("Terjadi kesalahan saat mengirim. Pastikan ID Channel benar dan Bot adalah Admin.")

# --- FUNGSI HAPUS ---
async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg_id = int(query.data.split("_")[1])
    
    # Cek apakah pengklik tombol adalah pemilik menfess
    if menfess_data.get(msg_id) == query.from_user.id:
        try:
            await context.bot.delete_message(chat_id=CHANNEL_ID, message_id=msg_id)
            await query.answer("Menfess berhasil dihapus dari channel!")
            await query.edit_message_text("✅ Menfess kamu telah dihapus dari channel.")
        except Exception:
            await query.answer("Gagal menghapus. Pesan mungkin sudah dihapus sebelumnya.", show_alert=True)
    else:
        await query.answer("❌ Kamu tidak bisa menghapus menfess orang lain!", show_alert=True)

# --- MAIN RUNNER ---
def main():
    if not TOKEN:
        print("BOT_TOKEN belum diatur di Railway Variables!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_menfess))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^del_"))
    
    print("Bot Menfess Gaydar berjalan...")
    app.run_polling()

if __name__ == '__main__':
    main()
