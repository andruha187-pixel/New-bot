import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from metar import get_metar, extract_temp
import state

# Включаем логирование, чтобы видеть ошибки в консоли Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Токен вашего бота
TOKEN = "8340766070:AAE2YKqhfhhegdZ4Kjm2zMk0UTg98DNtDd4"
STATION = "UUWW"

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start", callback_data="start")],
        [InlineKeyboardButton("⏸ Stop", callback_data="stop")],
        [InlineKeyboardButton("🌡 Latest", callback_data="latest")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.application.chat_ids.add(chat_id)
    await update.message.reply_text(
        "🌡 UUWW METAR Oracle ready",
        reply_markup=keyboard()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        state.tracking = True
        await query.edit_message_text("▶️ Tracking STARTED", reply_markup=keyboard())

    elif query.data == "stop":
        state.tracking = False
        await query.edit_message_text("⏸ Tracking STOPPED", reply_markup=keyboard())

    elif query.data == "latest":
        metar = get_metar(STATION)
        temp = extract_temp(metar) if metar else None
        await query.edit_message_text(
            f"🌡 UUWW:\n\nTemp: {temp}°C\n\n{metar}",
            reply_markup=keyboard()
        )

# Фоновая задача, которая вызывается планировщиком каждые 12 секунд
async def poller_job(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    if state.tracking:
        metar = get_metar(STATION)
        if metar:
            temp = extract_temp(metar)
            
            # Триггер срабатывает только если температура изменилась
            if temp is not None and temp != state.last_temp:
                state.last_temp = temp
                for chat_id in app.chat_ids:
                    try:
                        await app.bot.send_message(
                            chat_id=chat_id,
                            text=f"🌡 UUWW TEMP CHANGE:\n\n{temp}°C\n\n{metar}"
                        )
                    except Exception as e:
                        logging.error(f"Ошибка отправки в чат {chat_id}: {e}")

def main():
    # Собираем приложение бота
    app = Application.builder().token(TOKEN).build()
    app.chat_ids = set()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # Регистрируем фоновое задание в встроенный планировщик
    app.job_queue.run_repeating(poller_job, interval=12, first=5)

    print("Бот успешно запущен в режиме JobQueue...")
    app.run_polling()

if __name__ == "__main__":
    main()
