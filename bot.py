import asyncio
import json
import os
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiohttp import web

from config import *
import messages as msg


# ============================================================
# БАЗА ДАННЫХ
# ============================================================
def load_db():
    try:
        if not os.path.exists(DB_FILE):
            initial = {"users": [], "last_compliment": {}}
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(initial, f, ensure_ascii=False, indent=2)
            print(f"📁 Создан файл БД: {DB_FILE}")
            return initial
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ БД: {e}")
        return {"users": [], "last_compliment": {}}


def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Не сохранил БД: {e}")


def register_user(user_id):
    try:
        db = load_db()
        if user_id not in db["users"]:
            db["users"].append(user_id)
            save_db(db)
            print(f"✅ Новый пользователь: {user_id}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации: {e}")


# ============================================================
# УТИЛИТЫ
# ============================================================
def days_together():
    start = datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")
    delta = datetime.now() - start
    return delta.days


def days_to_event():
    event = datetime.strptime(DATE_EVENT, "%Y-%m-%d %H:%M")
    delta = event - datetime.now()
    if delta.total_seconds() < 0:
        return "🎉 Уже наступил!"
    return f"{delta.days} дней, {delta.seconds // 3600} часов"


def name_compliment(name):
    """Комплимент по буквам имени"""
    letters = {
        "а": "Ангельская",
        "б": "Бесподобная",
        "в": "Великолепная",
        "г": "Гениальная",
        "д": "Добрая",
        "е": "Единственная",
        "ж": "Желанная",
        "з": "Заботливая",
        "и": "Идеальная",
        "к": "Красивая",
        "л": "Любимая",
        "м": "Милая",
        "н": "Нежная",
        "о": "Очаровательная",
        "п": "Прекрасная",
        "р": "Роскошная",
        "с": "Солнечная",
        "т": "Тёплая",
        "у": "Умная",
        "ф": "Фантастическая",
        "х": "Хрупкая",
        "ц": "Ценная",
        "ч": "Чудесная",
        "ш": "Шикарная",
        "щ": "Щедрая",
        "э": "Элегантная",
        "ю": "Юная",
        "я": "Яркая",
    }
    name = name.lower().strip()
    result = []
    for letter in name:
        if letter in letters:
            result.append(f"<b>{letter.upper()}</b> — {letters[letter]}")
    if not result:
        return "Не могу составить комплимент из твоего имени, но ты всё равно самая лучшая 💕"
    return "💕 <b>Твоё имя — это комплимент:</b>\n\n" + "\n".join(result)


def main_menu():
    kb = [
        [KeyboardButton(text="💕 Комплимент"),    KeyboardButton(text="📅 Дней вместе")],
        [KeyboardButton(text="🤗 Обнимашка"),      KeyboardButton(text="💭 Скучаю")],
        [KeyboardButton(text="🎵 Песня дня"),      KeyboardButton(text="💌 Свидание")],
        [KeyboardButton(text="🍷 Рецепт"),          KeyboardButton(text="📸 Воспоминание")],
        [KeyboardButton(text="⏰ До вечера"),       KeyboardButton(text="🎯 Викторина")],
        [KeyboardButton(text="💗 Что я люблю"),    KeyboardButton(text="🌹 Почему люблю")],
        [KeyboardButton(text="💋 Флирт"),           KeyboardButton(text="🤗 Забота")],
        [KeyboardButton(text="🌅 Цитата"),          KeyboardButton(text="🎁 Сюрприз")],
        [KeyboardButton(text="🌸 Стих"),            KeyboardButton(text="🎬 Фильм на вечер")],
        [KeyboardButton(text="🍽️ Что приготовить"), KeyboardButton(text="💐 Комплимент по имени")],
        [KeyboardButton(text="🎂 До ДР"),           KeyboardButton(text="📞 Позвони мне")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ============================================================
# БОТ
# ============================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    register_user(message.from_user.id)

    text = (
        f"💕 <b>Привет, любимая!</b>\n\n"
        f"Это наш маленький бот-секрет. Тут я собрал кое-что для тебя:\n\n"
        f"💕 Комплименты\n"
        f"📅 Сколько мы вместе\n"
        f"🤗 Обнимашки\n"
        f"💭 Скучаю\n"
        f"🎵 Песня дня\n"
        f"💌 Идея свидания\n"
        f"🍷 Рецепт вечера\n"
        f"📸 Воспоминание\n"
        f"⏰ Обратный отсчёт\n"
        f"🎯 Викторина\n"
        f"💗 Что я люблю в тебе\n"
        f"🌹 Почему люблю\n"
        f"💋 Флирт\n"
        f"🤗 Забота\n"
        f"🌅 Цитата\n"
        f"🎁 Сюрприз\n"
        f"🌸 Стих\n"
        f"🎬 Фильм на вечер\n"
        f"🍽️ Что приготовить\n"
        f"💐 Комплимент по имени\n"
        f"🎂 До дня рождения\n"
        f"📞 Позвони мне\n\n"
        f"Жми на кнопки ниже 👇"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode=ParseMode.HTML)


# ============================================================
# ОСНОВНЫЕ КОМАНДЫ
# ============================================================

# 💕 Комплимент
@dp.message(Command("love"))
@dp.message(F.text == "💕 Комплимент")
async def cmd_love(message: Message):
    await message.answer(random.choice(msg.COMPLIMENTS))


# 📅 Дней вместе
@dp.message(Command("days"))
@dp.message(F.text == "📅 Дней вместе")
async def cmd_days(message: Message):
    d = days_together()
    text = (
        f"💕 Мы вместе уже <b>{d} дней</b>\n"
        f"Это {d // 30} месяцев и {d % 30} дней\n"
        f"Или {d * 24} часов вместе ❤️"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


# 🤗 Обнимашка
@dp.message(Command("hug"))
@dp.message(F.text == "🤗 Обнимашка")
async def cmd_hug(message: Message):
    await message.answer(msg.HUG_TEXT)
    try:
        await bot.send_message(
            YOUR_ID,
            "🤗 Она отправила тебе ОБНИМАШКУ!\n\nОбними её в ответ ❤️"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")


# 💭 Скучаю
@dp.message(Command("miss"))
@dp.message(F.text == "💭 Скучаю")
async def cmd_miss(message: Message):
    await message.answer(msg.MISS_TEXT)
    try:
        await bot.send_message(YOUR_ID, "💭 Она СКУЧАЕТ по тебе! Напиши ей прямо сейчас ❤️")
    except Exception as e:
        print(f"Ошибка: {e}")


# 🎵 Песня дня
@dp.message(Command("song"))
@dp.message(F.text == "🎵 Песня дня")
async def cmd_song(message: Message):
    await message.answer(random.choice(msg.SONGS))


# 💌 Свидание
@dp.message(Command("date"))
@dp.message(F.text == "💌 Свидание")
async def cmd_date(message: Message):
    await message.answer("💌 Идея для свидания:\n\n" + random.choice(msg.DATES))


# 🍷 Рецепт
@dp.message(Command("recipe"))
@dp.message(F.text == "🍷 Рецепт")
async def cmd_recipe(message: Message):
    await message.answer("🍷 Идея для вечера:\n\n" + random.choice(msg.RECIPES))


# 📸 Воспоминание
@dp.message(Command("memory"))
@dp.message(F.text == "📸 Воспоминание")
async def cmd_memory(message: Message):
    await message.answer(random.choice(msg.MEMORIES))


# ⏰ До вечера
@dp.message(Command("countdown"))
@dp.message(F.text == "⏰ До вечера")
async def cmd_countdown(message: Message):
    left = days_to_event()
    text = f"🍷 До нашего романтического вечера осталось:\n\n<b>{left}</b>\n\nГотовься, будет волшебно 💕"
    await message.answer(text, parse_mode=ParseMode.HTML)


# 🎯 Викторина
@dp.message(Command("quiz"))
@dp.message(F.text == "🎯 Викторина")
async def cmd_quiz(message: Message):
    q = random.choice(msg.QUIZ_QUESTIONS)
    text = f"🎯 <b>{q['q']}</b>\n\n"
    for i, a in enumerate(q["a"], 1):
        text += f"{i}. {a}\n"
    text += f"\nПравильный ответ: <b>{q['correct']}</b>"
    await message.answer(text, parse_mode=ParseMode.HTML)


# 💗 Что я люблю в тебе
@dp.message(Command("ilove"))
@dp.message(F.text == "💗 Что я люблю")
async def cmd_ilove(message: Message):
    await message.answer("💗 Что я люблю в тебе:\n\n" + random.choice(msg.LOVE_ABOUT_YOU))


# 🌹 Почему люблю
@dp.message(Command("why"))
@dp.message(F.text == "🌹 Почему люблю")
async def cmd_why(message: Message):
    await message.answer("🌹 Одна из причин, почему я тебя люблю:\n\n" + random.choice(msg.REASONS_LOVE))


# 💋 Флирт
@dp.message(Command("flirt"))
@dp.message(F.text == "💋 Флирт")
async def cmd_flirt(message: Message):
    await message.answer(random.choice(msg.FLIRTS))


# 🤗 Забота
@dp.message(Command("care"))
@dp.message(F.text == "🤗 Забота")
async def cmd_care(message: Message):
    await message.answer(random.choice(msg.CARE))


# 🌅 Цитата
@dp.message(Command("quote"))
@dp.message(F.text == "🌅 Цитата")
async def cmd_quote(message: Message):
    await message.answer(random.choice(msg.LOVE_QUOTES))


# 🎁 Сюрприз
@dp.message(Command("surprise"))
@dp.message(F.text == "🎁 Сюрприз")
async def cmd_surprise(message: Message):
    await message.answer(random.choice(msg.SURPRISES))


# 🌸 Стих
@dp.message(Command("poem"))
@dp.message(F.text == "🌸 Стих")
async def cmd_poem(message: Message):
    await message.answer(random.choice(msg.POEMS))


# 🎬 Фильм на вечер
@dp.message(Command("movie"))
@dp.message(F.text == "🎬 Фильм на вечер")
async def cmd_movie(message: Message):
    await message.answer("🎬 Идея для вечера:\n\n" + random.choice(msg.MOVIES))


# 🍽️ Что приготовить
@dp.message(Command("cook"))
@dp.message(F.text == "🍽️ Что приготовить")
async def cmd_cook(message: Message):
    await message.answer("🍽️ Идея для ужина:\n\n" + random.choice(msg.DINNER_IDEAS))


# 💐 Комплимент по имени
@dp.message(Command("name"))
@dp.message(F.text == "💐 Комплимент по имени")
async def cmd_name(message: Message):
    await message.answer(
        "Напиши своё имя — и я скажу, какая ты 💕\n\n"
        "Просто отправь имя следующим сообщением 👇"
    )
    # следующий текст от неё будет обработан ниже (см. обработчик fallback)


# 🎂 До ДР
@dp.message(Command("bday"))
@dp.message(F.text == "🎂 До ДР")
async def cmd_bday(message: Message):
    text = f"🎂 До твоего дня рождения осталось:\n\n<b>{msg.BDAY_COUNTDOWN}</b>\n\nГотовься принимать подарки 💕"
    await message.answer(text, parse_mode=ParseMode.HTML)


# 📞 Позвони мне
@dp.message(Command("call"))
@dp.message(F.text == "📞 Позвони мне")
async def cmd_call(message: Message):
    await message.answer("📞 Позвони мне, когда сможешь. Я жду 💕")
    try:
        await bot.send_message(YOUR_ID, "📞 Она просит ПОЗВОНИТЬ! Срочно! ❤️")
    except Exception as e:
        print(f"Ошибка: {e}")


# ============================================================
# FALLBACK — обработка имени (для комплимента по имени)
# ============================================================
@dp.message(F.text)
async def fallback_name(message: Message):
    """Ловит текст, который не подошёл под кнопки."""
    text = message.text.strip()

    # Если это короткое слово без спецсимволов — считаем его именем
    if 2 <= len(text) <= 20 and text.replace(" ", "").isalpha():
        await message.answer(name_compliment(text))
    else:
        await message.answer("Не понял команду 🤔 Жми кнопки ниже 👇", reply_markup=main_menu())


# ============================================================
# АВТО-РАССЫЛКА
# ============================================================
async def send_daily():
    """Каждый день в 9:00 / 12:00 / 22:00 — отправляет сообщение"""
    morning_sent = night_sent = compliment_sent = None
    today = datetime.now().date()

    while True:
        now = datetime.now()
        current_date = now.date()

        if current_date != today:
            morning_sent = night_sent = compliment_sent = None
            today = current_date

        hh_mm = now.strftime("%H:%M")

        # Утро
        if hh_mm == MORNING_TIME and morning_sent != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.MORNING))
                morning_sent = today
            except Exception as e:
                print(f"Ошибка утреннего: {e}")

        # Днём — комплимент
        if hh_mm == DAY_COMPLIMENT_TIME and compliment_sent != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.COMPLIMENTS))
                compliment_sent = today
            except Exception as e:
                print(f"Ошибка днём: {e}")

        # Вечер
        if hh_mm == NIGHT_TIME and night_sent != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.NIGHT))
                night_sent = today
            except Exception as e:
                print(f"Ошибка вечером: {e}")

        await asyncio.sleep(30)


# ============================================================
# ФЕЙКОВЫЙ ВЕБ-СЕРВЕР (для Render Web Service)
# ============================================================
async def healthcheck(request):
    return web.Response(text="Bot is alive ❤️")


async def start_webserver():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Веб-сервер на порту {port}")


# ============================================================
# MAIN
# ============================================================
async def main():
    asyncio.create_task(start_webserver())
    asyncio.create_task(send_daily())
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
