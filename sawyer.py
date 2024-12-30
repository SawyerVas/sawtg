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

# Хранилище для игры
game_data = {}

# Хранилище базы данных для проверки
DATABASE = []

# Загрузка базы данных из файла
def load_database(file_path="database.csv"):
    global DATABASE
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            DATABASE = [row for row in reader]
        logging.info("База данных успешно загружена.")
    except FileNotFoundError:
        logging.error("Файл базы данных не найден.")

# Проверка на совпадения
async def check_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text
    if not DATABASE:
        await update.message.reply_text("База данных пуста или не загружена.")
        return

    results = [row for row in DATABASE if query.lower() in row[0].lower()]
    if results:
        reply = "Найдено совпадение:\n" + "\n".join([", ".join(row) for row in results])
    else:
        reply = "Совпадений не найдено."

    await update.message.reply_text(reply)

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["/startgame", "/menu"], ["/help", "/stopgame"]]
        if user_id in game_data
        else [["/startgame", "/menu"], ["/help", "Проверить базу"]]
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
        "🔹 /echo [текст] - Повторю твое сообщение\n\n"
        "🔎 Проверка базы данных:\n"
        "🔹 Введите любой текст, чтобы проверить его в базе данных.\n"
        "⚙️ Дополнительные команды:\n"
        "🔹 /info - Информация о боте\n\n"
        "Если ты не помнишь команду или что-то непонятно, просто напиши мне, и я постараюсь помочь!"
    )

    # Проверим, есть ли активная игра
    user_id = update.message.from_user.id
    if user_id in game_data:
        help_text += "\n\n❗ Ты уже начал игру! Введи число, чтобы продолжить угадывать."

    await update.message.reply_text(help_text)

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["О боте", "Контакты"], ["Помощь", "Проверить базу"]]
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
        await update.message.reply_text("Введите текст для проверки в базе данных.")
    else:
        await check_database(update, context)

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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_number))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
