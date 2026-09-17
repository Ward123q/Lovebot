import asyncio
import json
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiohttp import web

from config import *
import messages as msg


# ============================================================
# БД
# ============================================================
def load_db():
    try:
        if not os.path.exists(DB_FILE):
            initial = {"users": [], "stats": {}, "mood": {}}
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(initial, f, ensure_ascii=False, indent=2)
            return initial
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ БД: {e}")
        return {"users": [], "stats": {}, "mood": {}}


def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ БД: {e}")


def register_user(user_id):
    try:
        db = load_db()
        if user_id not in db["users"]:
            db["users"].append(user_id)
            save_db(db)
            print(f"✅ Новый пользователь: {user_id}")
    except Exception as e:
        print(f"⚠️ {e}")


def add_stat(user_id, key):
    """Считает сколько раз пользователь жал кнопку"""
    try:
        db = load_db()
        stats = db.get("stats", {})
        user_stats = stats.get(str(user_id), {})
        user_stats[key] = user_stats.get(key, 0) + 1
        stats[str(user_id)] = user_stats
        db["stats"] = stats
        save_db(db)
    except Exception as e:
        print(f"⚠️ stat: {e}")


# ============================================================
# УТИЛИТЫ
# ============================================================
def days_together():
    start = datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")
    return (datetime.now() - start).days


def hours_together():
    start = datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")
    return int((datetime.now() - start).total_seconds() // 3600)


def minutes_together():
    start = datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")
    return int((datetime.now() - start).total_seconds() // 60)


def days_to_event():
    event = datetime.strptime(DATE_EVENT, "%Y-%m-%d %H:%M")
    delta = event - datetime.now()
    if delta.total_seconds() < 0:
        return "🎉 Уже наступил!"
    return f"{delta.days} дней, {delta.seconds // 3600} часов"


def days_to_bday():
    bday = datetime.strptime(HER_BIRTHDAY, "%Y-%m-%d")
    now = datetime.now()
    next_bday = bday.replace(year=now.year)
    if next_bday < now:
        next_bday = next_bday.replace(year=now.year + 1)
    delta = next_bday - now
    return f"{delta.days} дней"


def name_compliment(name):
    letters = {
        "а": "Ангельская", "б": "Бесподобная", "в": "Великолепная",
        "г": "Гениальная", "д": "Добрая", "е": "Единственная",
        "ж": "Желанная", "з": "Заботливая", "и": "Идеальная",
        "к": "Красивая", "л": "Любимая", "м": "Милая",
        "н": "Нежная", "о": "Очаровательная", "п": "Прекрасная",
        "р": "Роскошная", "с": "Солнечная", "т": "Тёплая",
        "у": "Умная", "ф": "Фантастическая", "х": "Хрупкая",
        "ц": "Ценная", "ч": "Чудесная", "ш": "Шикарная",
        "щ": "Щедрая", "э": "Элегантная", "ю": "Юная", "я": "Яркая",
    }
    result = [f"<b>{l.upper()}</b> — {letters[l]}" for l in name.lower().strip() if l in letters]
    if not result:
        return "Ты — самая лучшая 💕"
    return "💐 <b>Твоё имя — это комплимент:</b>\n\n" + "\n".join(result)


# ============================================================
# МЕНЮ
# ============================================================
def main_menu():
    kb = [
        [KeyboardButton(text="💕 Романтика"),   KeyboardButton(text="🎁 Сюрпризы")],
        [KeyboardButton(text="🎬 Развлечения"),  KeyboardButton(text="📅 Даты")],
        [KeyboardButton(text="🍽️ Быт"),          KeyboardButton(text="📊 Инфо")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_romance():
    kb = [
        [KeyboardButton(text="💕 Комплимент"), KeyboardButton(text="💐 По имени")],
        [KeyboardButton(text="🌸 Стих"),       KeyboardButton(text="🌹 Почему люблю")],
        [KeyboardButton(text="💗 Что я люблю"), KeyboardButton(text="💋 Флирт")],
        [KeyboardButton(text="🌅 Цитата"),      KeyboardButton(text="🤗 Забота")],
        [KeyboardButton(text="💌 Письмо"),      KeyboardButton(text="💍 Наше будущее")],
        [KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_surprise():
    kb = [
        [KeyboardButton(text="🎁 Сюрприз"),     KeyboardButton(text="🎲 Рулетка свиданий")],
        [KeyboardButton(text="🃏 Карта любви"), KeyboardButton(text="🎨 Открытка")],
        [KeyboardButton(text="😄 Анекдот"),     KeyboardButton(text="🎁 Подарок")],
        [KeyboardButton(text="🎭 Правда/Действие")],
        [KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_fun():
    kb = [
        [KeyboardButton(text="🎯 Викторина"),   KeyboardButton(text="🎬 Фильм")],
        [KeyboardButton(text="📺 Сериал"),       KeyboardButton(text="📚 Книга")],
        [KeyboardButton(text="🍽️ Что приготовить")],
        [KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_dates():
    kb = [
        [KeyboardButton(text="📅 Дней вместе"), KeyboardButton(text="⏰ До вечера")],
        [KeyboardButton(text="🎂 До ДР"),        KeyboardButton(text="💕 Всё время вместе")],
        [KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_life():
    kb = [
        [KeyboardButton(text="🤗 Обнимашка"),  KeyboardButton(text="💭 Скучаю")],
        [KeyboardButton(text="😘 Поцелуй"),    KeyboardButton(text="📞 Позвони мне")],
        [KeyboardButton(text="😴 Поспать"),     KeyboardButton(text="💧 Водичка")],
        [KeyboardButton(text="🍽️ Поела?"),      KeyboardButton(text="💪 Мотивашка")],
        [KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def menu_info():
    kb = [
        [KeyboardButton(text="📊 Моя статистика"), KeyboardButton(text="🏆 Достижения")],
        [KeyboardButton(text="📖 О боте"),          KeyboardButton(text="⬅️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ============================================================
# БОТ
# ============================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    register_user(message.from_user.id)
    await message.answer(
        "💕 <b>Привет, любимая!</b>\n\n"
        "Это наш маленький бот-секрет. Здесь я собрал кучу милых вещей только для тебя.\n\n"
        "Выбирай категорию 👇",
        reply_markup=main_menu(),
        parse_mode=ParseMode.HTML,
    )


@dp.message(Command("menu"))
@dp.message(F.text == "⬅️ Назад")
async def cmd_menu(message: Message):
    await message.answer("Главное меню 👇", reply_markup=main_menu())


# ============================================================
# РОМАНТИКА
# ============================================================
@dp.message(F.text == "💕 Романтика")
async def open_romance(message: Message):
    await message.answer("💕 Что хочешь?", reply_markup=menu_romance())


@dp.message(F.text == "💕 Комплимент")
async def m_compliment(message: Message):
    add_stat(message.from_user.id, "compliment")
    await message.answer(random.choice(msg.COMPLIMENTS))


@dp.message(F.text == "💐 По имени")
async def m_name(message: Message):
    await message.answer("💐 Напиши своё имя — и я скажу, какая ты 💕")


@dp.message(F.text == "🌸 Стих")
async def m_poem(message: Message):
    await message.answer(random.choice(msg.POEMS), parse_mode=ParseMode.HTML)


@dp.message(F.text == "🌹 Почему люблю")
async def m_why(message: Message):
    await message.answer("🌹 " + random.choice(msg.REASONS_LOVE))


@dp.message(F.text == "💗 Что я люблю")
async def m_ilove(message: Message):
    await message.answer(random.choice(msg.LOVE_ABOUT_YOU))


@dp.message(F.text == "💋 Флирт")
async def m_flirt(message: Message):
    await message.answer(random.choice(msg.FLIRTS))


@dp.message(F.text == "🌅 Цитата")
async def m_quote(message: Message):
    await message.answer(random.choice(msg.LOVE_QUOTES))


@dp.message(F.text == "🤗 Забота")
async def m_care(message: Message):
    await message.answer(random.choice(msg.CARE))


@dp.message(F.text == "💌 Письмо")
async def m_letter(message: Message):
    text = (
        "💌 <b>Письмо для тебя</b>\n\n"
        "<i>Любимая, я хочу сказать тебе кое-что важное.</i>\n\n"
        "<i>Ты — самое дорогое, что у меня есть. Каждый день с тобой — это подарок, "
        "и я не хочу тратить ни минуты на ссоры и обиды.</i>\n\n"
        "<i>Спасибо, что ты рядом. Спасибо за твоё терпение и любовь. "
        "Я обещаю быть лучше для тебя. И для нас.</i>\n\n"
        "<i>Ты — моё всё. Навсегда твой ❤️</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text == "💍 Наше будущее")
async def m_future(message: Message):
    await message.answer("💭 " + random.choice(msg.FUTURE_DREAMS))


# ============================================================
# СЮРПРИЗЫ
# ============================================================
@dp.message(F.text == "🎁 Сюрпризы")
async def open_surprise(message: Message):
    await message.answer("🎁 Что хочешь?", reply_markup=menu_surprise())


@dp.message(F.text == "🎁 Сюрприз")
async def m_surprise(message: Message):
    await message.answer(random.choice(msg.SURPRISES))


@dp.message(F.text == "🎲 Рулетка свиданий")
async def m_roulette(message: Message):
    await message.answer("🎲 Выпало:\n\n" + random.choice(msg.DATES))


@dp.message(F.text == "🃏 Карта любви")
async def m_card(message: Message):
    await message.answer(random.choice(msg.LOVE_CARDS))


@dp.message(F.text == "🎨 Открытка")
async def m_postcard(message: Message):
    await message.answer(random.choice(msg.CARDS), parse_mode=ParseMode.HTML)


@dp.message(F.text == "😄 Анекдот")
async def m_joke(message: Message):
    await message.answer(random.choice(msg.JOKES))


@dp.message(F.text == "🎁 Подарок")
async def m_gift(message: Message):
    await message.answer("🎁 Идея подарка:\n\n" + random.choice(msg.GIFT_IDEAS))


@dp.message(F.text == "🎭 Правда/Действие")
async def m_truth(message: Message):
    await message.answer(random.choice(msg.TRUTH_OR_DARE), parse_mode=ParseMode.HTML)


# ============================================================
# РАЗВЛЕЧЕНИЯ
# ============================================================
@dp.message(F.text == "🎬 Развлечения")
async def open_fun(message: Message):
    await message.answer("🎬 Что хочешь?", reply_markup=menu_fun())


@dp.message(F.text == "🎯 Викторина")
async def m_quiz(message: Message):
    add_stat(message.from_user.id, "quiz")
    q = random.choice(msg.QUIZ_QUESTIONS)
    text = f"🎯 <b>{q['q']}</b>\n\n"
    for i, a in enumerate(q["a"], 1):
        text += f"{i}. {a}\n"
    text += f"\nПравильный ответ: <b>{q['correct']}</b>"
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text == "🎬 Фильм")
async def m_movie(message: Message):
    await message.answer(random.choice(msg.MOVIES))


@dp.message(F.text == "📺 Сериал")
async def m_series(message: Message):
    await message.answer(random.choice(msg.SERIES))


@dp.message(F.text == "📚 Книга")
async def m_book(message: Message):
    await message.answer(random.choice(msg.BOOKS))


@dp.message(F.text == "🍽️ Что приготовить")
async def m_dinner(message: Message):
    await message.answer(random.choice(msg.DINNER_IDEAS))


# ============================================================
# ДАТЫ
# ============================================================
@dp.message(F.text == "📅 Даты")
async def open_dates(message: Message):
    await message.answer("📅 Что хочешь?", reply_markup=menu_dates())


@dp.message(F.text == "📅 Дней вместе")
async def m_days(message: Message):
    d = days_together()
    await message.answer(
        f"💕 Мы вместе уже <b>{d} дней</b>\n"
        f"Это {d // 30} месяцев и {d % 30} дней\n"
        f"Или {d * 24} часов вместе ❤️",
        parse_mode=ParseMode.HTML,
    )


@dp.message(F.text == "💕 Всё время вместе")
async def m_alltime(message: Message):
    await message.answer(
        f"⏳ <b>Мы вместе:</b>\n\n"
        f"📅 Дней: <b>{days_together()}</b>\n"
        f"⏰ Часов: <b>{hours_together()}</b>\n"
        f"⏱️ Минут: <b>{minutes_together()}</b>\n\n"
        f"И это только начало ♾️",
        parse_mode=ParseMode.HTML,
    )


@dp.message(F.text == "⏰ До вечера")
async def m_countdown(message: Message):
    left = days_to_event()
    await message.answer(
        f"🍷 До нашего романтического вечера осталось:\n\n<b>{left}</b>\n\nГотовься, будет волшебно 💕",
        parse_mode=ParseMode.HTML,
    )


@dp.message(F.text == "🎂 До ДР")
async def m_bday(message: Message):
    left = days_to_bday()
    await message.answer(
        f"🎂 До твоего дня рождения осталось:\n\n<b>{left}</b>\n\nГотовься принимать подарки 💕",
        parse_mode=ParseMode.HTML,
    )


# ============================================================
# БЫТ
# ============================================================
@dp.message(F.text == "🍽️ Быт")
async def open_life(message: Message):
    await message.answer("🍽️ Что хочешь?", reply_markup=menu_life())


@dp.message(F.text == "🤗 Обнимашка")
async def m_hug(message: Message):
    add_stat(message.from_user.id, "hug")
    await message.answer(msg.HUG_TEXT)
    try:
        await bot.send_message(YOUR_ID, "🤗 Она отправила тебе ОБНИМАШКУ! Обними в ответ ❤️")
    except: pass


@dp.message(F.text == "💭 Скучаю")
async def m_miss(message: Message):
    add_stat(message.from_user.id, "miss")
    await message.answer(msg.MISS_TEXT)
    try:
        await bot.send_message(YOUR_ID, "💭 Она СКУЧАЕТ! Напиши ей ❤️")
    except: pass


@dp.message(F.text == "😘 Поцелуй")
async def m_kiss(message: Message):
    await message.answer(msg.KISS_TEXT)
    try:
        await bot.send_message(YOUR_ID, "😘 Она послала тебе поцелуй! 💕")
    except: pass


@dp.message(F.text == "📞 Позвони мне")
async def m_call(message: Message):
    await message.answer("📞 Позвони мне, когда сможешь 💕")
    try:
        await bot.send_message(YOUR_ID, "📞 Она просит ПОЗВОНИТЬ! ❤️")
    except: pass


@dp.message(F.text == "😴 Поспать")
async def m_sleep(message: Message):
    await message.answer("😴 Иди поспи, любимая. Мир подождёт 💕")


@dp.message(F.text == "💧 Водичка")
async def m_water(message: Message):
    await message.answer("💧 Выпей водички, солнышко! Это важно 💕")


@dp.message(F.text == "🍽️ Поела?")
async def m_food(message: Message):
    await message.answer("🍽️ Ты поела? Если нет — иди поешь, я волнуюсь 💕")


@dp.message(F.text == "💪 Мотивашка")
async def m_motivation(message: Message):
    await message.answer(random.choice(msg.MOODS["грустно"] + msg.MOODS["устала"]))


# ============================================================
# ИНФО
# ============================================================
@dp.message(F.text == "📊 Инфо")
async def open_info(message: Message):
    await message.answer("📊 Что хочешь?", reply_markup=menu_info())


@dp.message(F.text == "📊 Моя статистика")
async def m_stats(message: Message):
    db = load_db()
    user_stats = db.get("stats", {}).get(str(message.from_user.id), {})
    if not user_stats:
        await message.answer("📊 Пока пусто! Жми кнопки — я считаю 😊")
        return
    text = "📊 <b>Твоя статистика:</b>\n\n"
    names = {"compliment": "💕 Комплименты", "hug": "🤗 Обнимашки", "miss": "💭 Скучала", "quiz": "🎯 Викторина"}
    total = 0
    for k, v in user_stats.items():
        text += f"{names.get(k, k)}: <b>{v}</b>\n"
        total += v
    text += f"\n💖 Всего: <b>{total}</b> действий"
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text == "🏆 Достижения")
async def m_achieve(message: Message):
    await message.answer(random.choice(msg.ACHIEVEMENTS))


@dp.message(F.text == "📖 О боте")
async def m_about(message: Message):
    await message.answer(
        "📖 <b>О боте</b>\n\n"
        "Этот бот сделан с любовью специально для тебя 💕\n\n"
        "Он умеет:\n"
        "• говорить комплименты\n"
        "• присылать стихи и цитаты\n"
        "• считать сколько мы вместе\n"
        "• предлагать идеи свиданий\n"
        "• заботиться о тебе\n"
        "• и ещё много всего!\n\n"
        "Исследуй все кнопки 💗",
        parse_mode=ParseMode.HTML,
    )


# ============================================================
# КОМПЛИМЕНТ ПО ИМЕНИ (fallback)
# ============================================================
@dp.message(F.text)
async def fallback_name(message: Message):
    text = message.text.strip()
    if 2 <= len(text) <= 20 and text.replace(" ", "").isalpha():
        await message.answer(name_compliment(text), parse_mode=ParseMode.HTML)
    else:
        await message.answer("Не понял 🤔 Жми кнопки 👇", reply_markup=main_menu())


# ============================================================
# АВТО-РАССЫЛКА
# ============================================================
async def send_daily():
    sent = {"m": None, "d": None, "n": None}
    today = datetime.now().date()
    while True:
        now = datetime.now()
        if now.date() != today:
            sent = {"m": None, "d": None, "n": None}
            today = now.date()
        hh_mm = now.strftime("%H:%M")
        if hh_mm == MORNING_TIME and sent["m"] != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.MORNING))
                sent["m"] = today
            except: pass
        if hh_mm == DAY_COMPLIMENT_TIME and sent["d"] != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.COMPLIMENTS))
                sent["d"] = today
            except: pass
        if hh_mm == NIGHT_TIME and sent["n"] != today:
            try:
                await bot.send_message(HER_ID, random.choice(msg.NIGHT))
                sent["n"] = today
            except: pass
        await asyncio.sleep(30)


# ============================================================
# ВЕБ-СЕРВЕР
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