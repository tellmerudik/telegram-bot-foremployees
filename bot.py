from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_url("ВСТАВЬ ССЫЛКУ НА ГУГЛ ТАБЛИЦУ").sheet1

# Глобальные переменные
user_data = {}
questions = [
    "Введите ваше ФИО.",
    "Введите вашу дату рождения.",
    "Введите ваш контактный телефон.",
    "Введите ваш email.",
    "Выберите отдел, в котором вы будете работать.",
    "Введите ваш город.",
    "Введите, как называется ваша должность.",
    "Введите фамилию вашего руководителя."
]
departments = ["Контроль качества", "IT", "Продажи", "Юридический", "Маркетинг", "Колл-центр", "HR"]

# Этап 1: Старт
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Добро пожаловать в СитиАрбитр! Этот бот поможет вам быстро освоить все аспекты работы в нашей команде.\n"
        "Прежде чем начать, заполните ваши данные.",
        reply_markup=ReplyKeyboardMarkup([["Начать"]], resize_keyboard=True)
    )

# Этап 2: Сбор данных
async def collect_data(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    chat_id = update.message.chat_id

    if chat_id not in user_data:
        user_data[chat_id] = {"step": 0}

    step = user_data[chat_id]["step"]

    if step < len(questions):
        if step == 4:  # Вопрос с выбором отдела
            await update.message.reply_text(
                questions[step],
                reply_markup=ReplyKeyboardMarkup([[d] for d in departments], resize_keyboard=True, one_time_keyboard=True)
            )
        else:
            if step > 0:
                user_data[chat_id][f"data_{step}"] = user_input
            await update.message.reply_text(questions[step])
        user_data[chat_id]["step"] += 1
    else:
        user_data[chat_id][f"data_{step}"] = user_input
        await confirm_data(update, context)

# Этап 3: Подтверждение данных
async def confirm_data(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    collected_data = user_data[chat_id]

    confirmation_message = (
        "Проверьте, пожалуйста, правильность ваших данных:\n\n"
        f"ФИО: {collected_data.get('data_1')}\n"
        f"Дата рождения: {collected_data.get('data_2')}\n"
        f"Контактный телефон: {collected_data.get('data_3')}\n"
        f"Email: {collected_data.get('data_4')}\n"
        f"Отдел: {collected_data.get('data_5')}\n"
        f"Город: {collected_data.get('data_6')}\n"
        f"Должность: {collected_data.get('data_7')}\n"
        f"Фамилия руководителя: {collected_data.get('data_8')}"
    )
    await update.message.reply_text(
        confirmation_message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Всё верно", callback_data="confirm"),
             InlineKeyboardButton("❌ Ввести данные заново", callback_data="redo")]
        ])
    )

# Обработка кнопок подтверждения данных
async def handle_confirmation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == "confirm":
        collected_data = user_data[chat_id]
        # Сохранение данных в Google Sheets
        sheet.append_row([
            collected_data.get('data_1'), collected_data.get('data_2'),
            collected_data.get('data_3'), collected_data.get('data_4'),
            collected_data.get('data_5'), collected_data.get('data_6'),
            collected_data.get('data_7'), collected_data.get('data_8')
        ])
        await query.message.reply_text("Данные сохранены. Переходим к следующему этапу!")
        await company_info(query, context)
    elif query.data == "redo":
        user_data[chat_id]["step"] = 0
        await query.message.reply_text("Хорошо, начнём заново. Введите ваше ФИО.")

# Этап 4: Обучение о компании
async def company_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Мы — СитиАрбитр. Мы работаем профессионально и честно, чтобы наши клиенты жили счастливо и финансово свободно.\n"
        "Наш основной продукт — процедура банкротства для физических лиц, но также мы предлагаем...",
        reply_markup=ReplyKeyboardMarkup([["Интересно! А кто придумал такую компанию?"]], resize_keyboard=True)
    )

async def founder_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Основатель компании — Сизов Борис Георгиевич.\n"
        "'Мне хотелось создать компанию с культурой, где сотрудники свободны, творят, и при этом испытывают больше счастья и совместно больше зарабатывают.\n"
        "Фокус на свободе, реализации и удовольствии.'",
        reply_markup=ReplyKeyboardMarkup([["Здорово! А как развивалась компания?"]], resize_keyboard=True)
    )

async def history_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "📍 За год до старта у нас появилась мечта создать компанию, которая реально помогает людям и работает честно и открыто.\n"
        "📅 29 апреля 2019 года мы открыли компанию и начали наш путь.\n"
        "📅 В марте 2020 года пандемия изменила всё. Мы быстро адаптировались к дистанционной работе, благодаря чему смогли расширить клиентскую базу.\n"
        "🔄 Летом 2020 года обновили отдел продаж, что стало точкой роста.\n"
        "🎉 В 2022 году отметили 1000 клиентов и открыли первый региональный офис в Кирове.\n"
        "📊 В 2024 году открыли бэк-офис в Челябинске и два новых офиса в других городах.",
        reply_markup=ReplyKeyboardMarkup([["Интересно! А в каких городах открыты офисы?"]], resize_keyboard=True)
    )

async def geography_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Наши офисы находятся в:\n"
        "- Киров\n"
        "- Кирово-Чепецк\n"
        "- Самара\n"
        "- Пермь\n"
        "- Челябинск (бэк-офис)\n"
        "- Москва",
        reply_markup=ReplyKeyboardMarkup([["Впечатляет! А как устроено взаимодействие между отделами?"]], resize_keyboard=True)
    )

async def structure_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "У нас есть топ-менеджеры, которые направляют и контролируют работу. "
        "Также есть сотрудники, которые воплощают задачи в жизнь.\n\n"
        "Вот структура компании, которая показывает, как всё устроено.",
        reply_markup=ReplyKeyboardMarkup([["Есть ещё что-то, что я должен знать о компании?"]], resize_keyboard=True)
    )

# Этап 5: Завершение обучения
async def final_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Да, я отправляю тебе ссылку на документ, где собрана вся информация о нас. Там ты найдёшь:\n"
        "- Бонусы для сотрудников\n"
        "- Полезные ресурсы\n"
        "- Даты выплаты зарплаты.",
        reply_markup=ReplyKeyboardMarkup([["Ознакомился!"]], resize_keyboard=True)
    )

# Тестовые вопросы

# Вопрос 1
async def question_one(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Прекрасно! Задам несколько вопросов, чтобы убедиться, что ты всё понял, и пойдём дальше.\n\n"
        "Вопрос 1: В каком году основали компанию?"
    )

async def handle_question_one(update: Update, context: CallbackContext) -> None:
    if update.message.text.strip() == "2019":
        await update.message.reply_text("Верно! Переходим к следующему вопросу.")
        await question_two(update, context)
    else:
        await update.message.reply_text("Неправильно. Попробуй ещё раз. В каком году основали компанию?")

# Вопрос 2
async def question_two(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Вопрос 2: Когда в компании выплачивают ЗП?\n"
        "Введи две цифры через пробел (например: 25 10)."
    )

async def handle_question_two(update: Update, context: CallbackContext) -> None:
    correct_answers = ["25 10", "10 25"]
    if update.message.text.strip() in correct_answers:
        await update.message.reply_text("Отлично! Ты всё правильно понял!")
        await finish_training(update, context)
    else:
        await update.message.reply_text("Неправильно. Попробуй ещё раз. Когда в компании выплачивают ЗП?")

# Завершение обучения
async def finish_training(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Поздравляю! Ты успешно прошёл(а) обучение и готов(а) приступить к работе! "
        "Если у тебя будут вопросы, бот всегда готов помочь. Удачи!"
    )

# Запуск приложения
if __name__ == "__main__":
    application = ApplicationBuilder().token("ВАШ_ТОКЕН_БОТА").build()

    # Основные этапы
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_data))
    application.add_handler(CallbackQueryHandler(handle_confirmation, pattern="confirm|redo"))

    # Обучение
    application.add_handler(MessageHandler(filters.Regex("Интересно!"), founder_info))
    application.add_handler(MessageHandler(filters.Regex("Здорово!"), history_info))
    application.add_handler(MessageHandler(filters.Regex("Впечатляет!"), structure_info))
    application.add_handler(MessageHandler(filters.Regex("Ознакомился!"), final_info))

    # Тестовые вопросы
    application.add_handler(MessageHandler(filters.Regex("^В каком году основали компанию\\?$"), question_one))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question_one))
    application.add_handler(MessageHandler(filters.Regex("^Когда в компании выплачивают ЗП\\?$"), question_two))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question_two))

    application.run_polling()


# Добавить остальные этапы по аналогии выше

