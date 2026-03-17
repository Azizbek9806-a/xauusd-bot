import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены и ID из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', '0'))

if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

if YOUR_USER_ID == 0:
    logger.warning("YOUR_USER_ID не установлен, пересылка не будет работать")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-помощник для торговли XAUUSD.\n"
        "Отправляй мне скриншоты графиков, и я буду их анализировать.\n"
        "Команды:\n"
        "/start - это сообщение\n"
        "/help - помощь"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь мне скриншот графика XAUUSD с отмеченными уровнями.\n"
        "Я перешлю его Азизбеку и помогу с анализом."
    )

# Обработка фото
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
            caption=f"📸 Скриншот от @{update.effective_user.username or 'пользователя'}"
        )
        await update.message.reply_text("✅ Скриншот отправлен Азизбеку!")
    except Exception as e:
        logger.error(f"Ошибка при пересылке: {e}")
        await update.message.reply_text("❌ Не удалось отправить скриншот")

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower() in ['/start', '/help']:
        return
    await update.message.reply_text(f"Сообщение получено. Используй /help для списка команд.")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Ошибка: %s", context.error)

def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    
    logger.info("Бот запущен и готов к работе")
    app.run_polling()

if __name__ == '__main__':
    main()
