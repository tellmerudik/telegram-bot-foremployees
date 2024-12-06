import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Этапы диалога
FIO, DOB, DEPARTMENT, CITY, POSITION, SUPERVISOR, EMAIL, PHONE, CONFIRM = range(9)

# Переменная для временного хранения данных
user_data = {}

# Команда /start
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Добро пожаловать! Пожалуйста, введите ваше ФИО.")
    return FIO

# Этап ввода ФИО
async def get_fio(update: Update, context: CallbackContext) -> int:
    user_data['fio'] = update.message.text
    await update.message.reply_text("Введите вашу дату рождения (в формате ДД.ММ.ГГГГ).")
    return DOB

# Этап ввода даты рождения
async def get_dob(update: Update, context: CallbackContext) -> int:
    user_data['dob'] = update.message.text
    keyboard = [
        [KeyboardButton("Продажи"), KeyboardButton("Маркетинг")],
        [KeyboardButton("Юридический"), KeyboardButton("HR")],
        [KeyboardButton("Контроль качества"), KeyboardButton("ИТ")],
        [KeyboardButton("Колл-центр")],
    ]
    await update.message.reply_text(
        "Укажите ваш отдел, выбрав из предложенных вариантов:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return DEPARTMENT

# Этап ввода отдела
async def get_department(update: Update, context: CallbackContext) -> int:
    user_data['department'] = update.message.text
    await update.message.reply_text("Введите ваш город.")
    return CITY

# Этап ввода города
async def get_city(update: Update, context: CallbackContext) -> int:
    user_data['city'] = update.message.text
    await update.message.reply_text("Введите вашу должность.")
    return POSITION

# Этап ввода должности
async def get_position(update: Update, context: CallbackContext) -> int:
    user_data['position'] = update.message.text
    await update.message.reply_text("Введите фамилию вашего руководителя.")
    return SUPERVISOR

# Этап ввода фамилии руководителя
async def get_supervisor(update: Update, context: CallbackContext) -> int:
    user_data['supervisor'] = update.message.text
    await update.message.reply_text("Введите ваш email.")
    return EMAIL

# Этап ввода email
async def get_email(update: Update, context: CallbackContext) -> int:
    user_data['email'] = update.message.text
    await update.message.reply_text("Введите ваш номер телефона.")
    return PHONE

# Этап ввода телефона
async def get_phone(update: Update, context: CallbackContext) -> int:
    user_data['phone'] = update.message.text

    # Итоговое подтверждение данных
    confirmation_message = (
        "Проверьте, пожалуйста, правильность введенных данных:\n\n"
        f"ФИО: {user_data['fio']}\n"
        f"Дата рождения: {user_data['dob']}\n"
        f"Отдел: {user_data['department']}\n"
        f"Город: {user_data['city']}\n"
        f"Должность: {user_data['position']}\n"
        f"Руководитель: {user_data['supervisor']}\n"
        f"Email: {user_data['email']}\n"
        f"Телефон: {user_data['phone']}\n\n"
        "Если все верно, нажмите ✅ Подтвердить. Если нужно изменить, нажмите ❌ Ввести заново."
    )
    keyboard = [
        [KeyboardButton("✅ Подтвердить"), KeyboardButton("❌ Ввести заново")]
    ]
    await update.message.reply_text(confirmation_message, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return CONFIRM

# Этап подтверждения данных
async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text == "✅ Подтвердить":
        await update.message.reply_text("Спасибо! Ваши данные записаны. Бот завершил работу.")
        # Здесь можно добавить логику для сохранения данных в Google Таблицу
        return ConversationHandler.END
    else:
        await update.message.reply_text("Начнем заново. Пожалуйста, введите ваше ФИО.")
        return FIO

# Отмена
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Вы отменили заполнение данных. Если захотите начать заново, введите /start.")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dob)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
            SUPERVISOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_supervisor)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()
