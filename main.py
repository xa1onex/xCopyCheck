import os
import sys
import signal
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import difflib

# Имя файла для хранения PID
PID_FILE = "bot.pid"

# Удаляем PID-файл при завершении
def clean_up():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

# Настраиваем обработчики сигналов
def handle_exit(signum, frame):
    clean_up()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Проверяем, запущен ли процесс
if os.path.exists(PID_FILE):
    with open(PID_FILE, "r") as f:
        existing_pid = int(f.read().strip())
    try:
        os.kill(existing_pid, 0)  # Проверяем, активен ли процесс
        print("Бот уже запущен! Завершение...")
        sys.exit(1)
    except OSError:
        print("Старый PID найден, но процесс не активен. Удаляю файл...")
        os.remove(PID_FILE)

# Записываем текущий PID в файл
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

# Хранение текстов для сравнения
texts = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
        [KeyboardButton("🆕 Сброс")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "👋 *Привет!*\n\n"
        "Отправь мне два текста по очереди, и я покажу, чем они отличаются. "
        "Используйте кнопки ниже для управления.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Обработка текстов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not text.strip():
        await update.message.reply_text("❗️ Текст не может быть пустым. Пожалуйста, отправьте текст.")
        return

    if user_id not in texts:
        texts[user_id] = [text]
        await update.message.reply_text("✅ Первый текст сохранен. Теперь отправьте второй текст.")
    elif len(texts[user_id]) == 1:
        texts[user_id].append(text)
        differences = compare_texts(texts[user_id][0], texts[user_id][1])

        if differences:
            await update.message.reply_text(
                f"🔍 *Различия между текстами:*\n\n{differences}",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("🎉 Тексты полностью совпадают!")

        # Клавиатура после сравнения
        keyboard = [
            [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
            [KeyboardButton("🆕 Сбросить")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            "Вы можете начать заново, отправив новый текст или получить помощь.",
            reply_markup=reply_markup
        )
        texts.pop(user_id)  # Очищаем данные
    else:
        await update.message.reply_text("❗️ Что-то пошло не так. Напишите /reset, чтобы начать заново.")

# Сравнение текстов с подчеркиванием различий
def compare_texts(text1, text2):
    diff = difflib.ndiff(text1, text2)
    result = []
    for i in diff:
        if i.startswith("- "):
            result.append(f"<u>{i[2:]}</u>")
        elif i.startswith("+ "):
            result.append(f"<u>{i[2:]}</u>")
        else:
            result.append(i[2:])
    return "".join(result) or "Тексты совпадают или не содержат различий."

# Основная функция
def main():
    app = Application.builder().token("7709470340:AAH3M8YTcub5-6zUO0rOr6TwJloF448DjsE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

# Запуск бота
if __name__ == "__main__":
    try:
        main()
    finally:
        clean_up()