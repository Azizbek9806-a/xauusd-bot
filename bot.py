import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', '0'))

if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для торговли XAUUSD.\n"
        "Отправляй скриншоты графиков."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь мне скриншот графика, я перешлю его Азизбеку."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Получено фото от %s", update.effective_user.id)
    
    if YOUR_USER_ID == 0:
        await update.message.reply_text("Ошибка: не указан ID получателя")
        return
    
    photo_file = await update.message.photo[-1].get_file()
    
    try:
        await context.bot.send_photo(
            chat_id=YOUR_USER_ID,
            photo=photo_file.file_id,
            caption=f"📸 Скриншот от @{update.effective_user.username}"
        )
        await update.message.reply_text("✅ Скриншот отправлен!")
    except Exception as e:
        logger.error(f"Ошибка при пересылке: {e}")
        await update.message.reply_text("❌ Не удалось отправить скриншот")

def main():
    logger.info("Запуск бота...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()
