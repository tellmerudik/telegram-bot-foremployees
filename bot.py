import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Добро пожаловать! Пожалуйста, введите ваше ФИО.")

async def echo(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    await update.message.reply_text(f"Вы ввели: {user_input}")

if __name__ == '__main__':
  application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()
