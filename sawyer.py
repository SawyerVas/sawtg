from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import random
import logging

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Токен вашего бота
TOKEN = "7907843779:AAHweV-VrnluOt-rK-tDlM2EuFEo5oMyTBQ"

# Хранилище для игры
game_data = {}

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["/startgame", "/menu"], ["/help", "/stopgame"]]
        if user_id in game_data
        else [["/startgame", "/menu"], ["/help"]]
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
        "⚙️ Дополнительные команды:\n"
        "🔹 /info - Информация о боте\n\n"
        "Если ты не помнишь команду или что-то непонятно, просто напиши мне, и я постараюсь помочь!"
    )

    user_id = update.message.from_user.id
    if user_id in game_data:
        help_text += "\n\n❗ Ты уже начал игру! Введи число, чтобы продолжить угадывать."

    # Добавляем интерактивное меню для помощи
    keyboard = [
        [InlineKeyboardButton("Как начать игру?", callback_data="help_startgame")],
        [InlineKeyboardButton("Как остановить игру?", callback_data="help_stopgame")],
        [InlineKeyboardButton("Общение с ботом", callback_data="help_communication")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(help_text, reply_markup=reply_markup)

# Функция для обработки кнопок помощи
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "help_startgame":
        await query.edit_message_text(
            "Чтобы начать игру, введите /startgame. Бот загадает число, и вы должны его угадать!"
        )
    elif query.data == "help_stopgame":
        await query.edit_message_text(
            "Чтобы остановить текущую игру, введите /stopgame. Ваш прогресс будет сброшен."
        )
    elif query.data == "help_communication":
        await query.edit_message_text(
            "Вы можете общаться с ботом, отправляя текстовые сообщения или команды, такие как /echo [текст]."
        )

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    keyboard = (
        [["О боте", "Контакты"], ["Помощь", "Остановить игру"]]
        if user_id in game_data
        else [["Начать игру", "О боте", "Контакты"], ["Помощь"]]
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
    else:
        await update.message.reply_text(f"Вы сказали: {update.message.text}")

# Функция для обработки ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Произошла ошибка: %s", context.error)
    if update:
        await update.message.reply_text("Упс! Что-то пошло не так.")

# Основная функция
def main():
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
    application.add_handler(MessageHandler(filters.Regex("^/help"), help_callback))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
