# bot.py
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from main import InstagramAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analyzer = InstagramAnalyzer()

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Укажите username: /scan username")
        return

    username = context.args[0].lstrip('@')
    await update.message.reply_text(f"🚀 Начинаю анализ @{username} ...")
    context.application.create_task(run_analysis(update, username))

async def run_analysis(update: Update, username: str):
    try:
        analyzer.process_username(username, limit=5)
        await update.message.reply_text("✅ Анализ завершен.")
    except Exception as e:
        logger.exception("Ошибка анализа")
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    token = os.getenv("INSTABOT_TOKEN")
    if not token:
        print("❌ Не задан INSTABOT_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("scan", scan))
    app.run_polling()

if __name__ == "__main__":
    main()


