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

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

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
    
    if "chat_ids" not in context.application.bot_data:
        context.application.bot_data["chat_ids"] = set()
    context.application.bot_data["chat_ids"].add(chat_id)

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

async def poller_job(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    if state.tracking:
        metar = get_metar(STATION)
        if metar:
            temp = extract_temp(metar)
            
            if temp is not None and temp != state.last_temp:
                state.last_temp = temp
                
                chat_ids = app.bot_data.get("chat_ids", set())
                for chat_id in chat_ids:
                    try:
                        await app.bot.send_message(
                            chat_id=chat_id,
                            text=f"🌡 UUWW TEMP CHANGE:\n\n{temp}°C\n\n{metar}"
                        )
                    except Exception as e:
                        logging.error(f"Ошибка отправки в чат {chat_id}: {e}")

async def main_async():
    # Инициализируем приложение внутри асинхронного контекста
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.job_queue.run_repeating(poller_job, interval=12, first=5)

    # Правильный асинхронный запуск без run_polling()
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print("Бот успешно запущен в асинхронном режиме...")
        
        # Держим бота запущенным бесконечно
        while True:
            await asyncio.sleep(3600)

def main():
    # Используем современный asyncio.run для управления циклом событий
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
    
