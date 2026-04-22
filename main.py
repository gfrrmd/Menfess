import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Variabel dari Railway
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

menfess_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Selamat datang di Bot Menfess Gaydar!.\n\n"
        "Kirim pesan dengan awalan "mfs!" agar pesanmu terkirim ke channel.\n"
        "Contoh: "mfs! Halo semuanya salam kenal.\n\n"
        "Kamu juga bisa kirim Foto, Video, dan Media lainnya, pastikan memakai awalan "mfs!" yaa!"
        
    )

async def handle_menfess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    
    user_id = msg.from_user.id
    username = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name
    
    # Ambil teks dari pesan atau caption media
    text_content = msg.text or msg.caption or ""
    
    if not text_content.startswith("mfs!"):
        return

    clean_content = text_content.replace("mfs!", "", 1).strip()
    
    try:
        # Kirim ke Channel
        if msg.text:
            sent_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=clean_content)
        elif msg.photo:
            sent_msg = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=msg.photo[-1].file_id, caption=clean_content)
        elif msg.video:
            sent_msg = await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption=clean_content)
        elif msg.voice:
            sent_msg = await context.bot.send_voice(chat_id=CHANNEL_ID, voice=msg.voice.file_id, caption=clean_content)
        else:
            await msg.reply_text("Media tidak didukung.")
            return

        # Format Link Channel (Menghapus -100 agar link bisa diklik)
        clean_ch_id = str(CHANNEL_ID).replace("-100", "")
        channel_link = f"https://t.me/c/{clean_ch_id}/{sent_msg.message_id}"
        
        menfess_data[sent_msg.message_id] = user_id

        # Balasan ke user
        keyboard = [[InlineKeyboardButton("🗑️ Hapus Menfess", callback_data=f"del_{sent_msg.message_id}")]]
        await msg.reply_text(
            f"✅ **Terkirim!**\nLihat di: [Klik Disini]({channel_link})",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        # Laporan ke Admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 **Log Menfess**\nDari: {username} (`{user_id}`)\nLink: {channel_link}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.reply_text("Gagal mengirim. Cek apakah Bot sudah jadi Admin di Channel.")

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    msg_id = int(data[1])
    
    if menfess_data.get(msg_id) == query.from_user.id:
        try:
            await context.bot.delete_message(chat_id=CHANNEL_ID, message_id=msg_id)
            await query.edit_message_text("✅ Menfess telah dihapus.")
        except:
            await query.answer("Gagal menghapus pesan di channel.", show_alert=True)
    else:
        await query.answer("Bukan menfess milikmu!", show_alert=True)

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN tidak ditemukan di Environment Variables!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_menfess))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^del_"))
    
    app.run_polling()

if __name__ == '__main__':
    main()
