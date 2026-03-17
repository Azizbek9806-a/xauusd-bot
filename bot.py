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

# Хранилище для ID чатов пользователей, которые начали диалог
user_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_chats[user_id] = chat_id  # Сохраняем, чтобы знать, куда отвечать
    await update.message.reply_text(
        "Привет! Я бот для торговли XAUUSD.\n"
        "Отправляй скриншоты графиков, и аналитик ответит тебе сюда же."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_chats[user_id] = chat_id  # Обновляем на всякий случай
    
    logger.info(f"Получено фото от {user_id}")
    
    if YOUR_USER_ID == 0:
        await update.message.reply_text("Ошибка: не указан ID получателя")
        return
    
    photo_file = await update.message.photo[-1].get_file()
    
    # Пересылаем фото тебе (в DeepSeek чат)
    await context.bot.send_photo(
        chat_id=YOUR_USER_ID,
        photo=photo_file.file_id,
        caption=f"📸 Скриншот от @{update.effective_user.username} (ID: {user_id})"
    )
    await update.message.reply_text("✅ Скриншот отправлен аналитику! Жди ответа.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_chats[user_id] = chat_id
    
    # Игнорируем команды
    if update.message.text.startswith('/'):
        return
    
    # Пересылаем текст мне
    await context.bot.send_message(
        chat_id=YOUR_USER_ID,
        text=f"💬 Сообщение от @{update.effective_user.username} (ID: {user_id}):\n{update.message.text}"
    )
    await update.message.reply_text("✅ Сообщение отправлено аналитику. Скоро отвечу.")

# Функция, которую я буду вызывать (она будет добавлена позже)
# Но пока бот просто принимает сообщения

def main():
    logger.info("Запуск бота...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Бот запущен и ждёт сообщения")
    app.run_polling()

if __name__ == '__main__':
    main()
