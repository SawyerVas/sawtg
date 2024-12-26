from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import random

# Токен вашего бота
TOKEN = "7907843779:AAHweV-VrnluOt-rK-tDlM2EuFEo5oMyTBQ"

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я ваш бот. Чем могу помочь?")

# Функция для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Доступные команды:\n"
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/info - Информация о боте\n"
        "/echo [текст] - Повторить сообщение\n"
    )
    await update.message.reply_text(help_text)

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ["О боте", "Контакты"],
        ["Помощь"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)    

# Хранилище для игры
game_data = {}

# Команда /startgame
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    number = random.randint(1, 100)
    game_data[user_id] = number

    await update.message.reply_text("Я загадал число от 1 до 100. Попробуйте угадать!")

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
    await update.message.reply_text(f"Вы сказали: {update.message.text}")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))  # Регистрация команды /help
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("startgame", start_game))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_number))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
