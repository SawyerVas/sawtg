from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import random
import logging
import csv

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Токен вашего бота
TOKEN = "7907843779:AAHweV-VrnluOt-rK-tDlM2EuFEo5oMyTBQ"

# Хранилище для игры и базы данных
game_data = {}
database = []

# Функция загрузки базы данных
def load_database(file_path="database.csv"):
    global database
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            database = [row for row in reader]
        logging.info("База данных успешно загружена.")
    except FileNotFoundError:
        logging.error("Файл базы данных не найден.")
        database = []
    except Exception as e:
        logging.error(f"Ошибка при загрузке базы данных: {e}")
        database = []

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["/startgame", "/menu"], ["/help", "/stopgame", "/check"]]
        if user_id in game_data
        else [["/startgame", "/menu"], ["/help", "/check"]]
    )
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я ваш бот. Чем могу помочь?", reply_markup=reply_markup
    )

# Функция для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "👋 Привет! Я ваш бот. Вот что я могу:\n\n"
        "🔹 /start - Запуск бота\n"
        "🔹 /help - Помощь (ты сейчас читаешь это)\n"
        "🔹 /menu - Открывает главное меню с опциями\n\n"
        "🎮 Игры:\n"
        "🔹 /startgame - Начать игру в угадывание числа (Я загадаю число от 1 до 100)\n"
        "🔹 /stopgame - Остановить игру\n\n"
        "💬 Команды для общения:\n"
        "🔹 /echo [текст] - Повторю твое сообщение\n"
        "🔹 /check [запрос] - Проверю запрос в базе данных\n\n"
        "⚙️ Дополнительные команды:\n"
        "🔹 /info - Информация о боте\n"
        "🔹 /reload_database - Перезагрузить базу данных (для администраторов)\n\n"
        "Если ты не помнишь команду или что-то непонятно, просто напиши мне, и я постараюсь помочь!"
    )

    user_id = update.message.from_user.id
    if user_id in game_data:
        help_text += "\n\n❗ Ты уже начал игру! Введи число, чтобы продолжить угадывать."

    await update.message.reply_text(help_text)

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["О боте", "Контакты"], ["Помощь", "Остановить игру", "Проверить базу"]]
        if user_id in game_data
        else [["Начать игру", "О боте", "Контакты"], ["Помощь", "Проверить базу"]]
    )
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

# Команда /startgame
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in game_data:
        await update.message.reply_text("Вы уже начали игру! Попробуйте угадать число.")
        return

    number = random.randint(1, 100)
    game_data[user_id] = number
    await update.message.reply_text("Я загадал число от 1 до 100. Попробуйте угадать!")

# Команда /stopgame
async def stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in game_data:
        del game_data[user_id]
        await update.message.reply_text("Игра остановлена. Хотите сыграть еще?")
    else:
        await update.message.reply_text("Вы не начинали игру.")

# Команда /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Пожалуйста, укажите запрос для проверки. Например: /check запрос")
        return

    matches = [row for row in database if query.lower() in " ".join(row).lower()]
    if matches:
        response = "Совпадения найдены:\n" + "\n".join([", ".join(row) for row in matches])
    else:
        response = "Совпадений не найдено."

    await update.message.reply_text(response)

# Команда /reload_database
async def reload_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    load_database()
    await update.message.reply_text("База данных перезагружена.")

# Обработка попыток
async def guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    guess = update.message.text

    if user_id not in game_data:
        await update.message.reply_text("Начните игру с команды /startgame.")
        return

    try:
        guess = int(guess)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return

    number = game_data[user_id]
    if guess < number:
        await update.message.reply_text("Больше!")
    elif guess > number:
        await update.message.reply_text("Меньше!")
    else:
        await update.message.reply_text("Поздравляю! Вы угадали число!")
        del game_data[user_id]

# Функция для обработки текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.lower() in ["о боте", "контакты"]:
        await update.message.reply_text("Я простой бот, созданный для демонстрации.")
    elif update.message.text.lower() == "помощь":
        await help_command(update, context)
    elif update.message.text.lower() == "проверить базу":
        await update.message.reply_text("Введите команду /check [запрос] для поиска в базе данных.")
    else:
        await update.message.reply_text(f"Вы сказали: {update.message.text}")

# Функция для обработки ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Произошла ошибка: %s", context.error)
    if update:
        await update.message.reply_text("Упс! Что-то пошло не так.")

# Основная функция
def main():
    # Загрузка базы данных
    load_database()

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("startgame", start_game))
    application.add_handler(CommandHandler("stopgame", stop_game))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("reload_database", reload_database))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_number))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
