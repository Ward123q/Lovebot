import asyncio
import json
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

from config import *
import messages as msg


# ============================================================
# БАЗА ДАННЫХ (простой JSON)
# ============================================================
import os
import json

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


def main_menu():
    kb = [
        [KeyboardButton(text="💕 Комплимент"), KeyboardButton(text="📅 Дней вместе")],
        [KeyboardButton(text="🤗 Обнимашка"),   KeyboardButton(text="💭 Скучаю")],
        [KeyboardButton(text="🎵 Песня дня"),   KeyboardButton(text="💌 Свидание")],
        [KeyboardButton(text="🍷 Рецепт"),       KeyboardButton(text="📸 Воспоминание")],
        [KeyboardButton(text="⏰ До вечера"),    KeyboardButton(text="🎯 Викторина")],
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
        f"⏰ Обратный отсчёт до вечера\n"
        f"🎯 Викторина\n\n"
        f"Жми на кнопки ниже 👇"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode=ParseMode.HTML)


# /love или кнопка Комплимент
@dp.message(Command("love"))
@dp.message(F.text == "💕 Комплимент")
async def cmd_love(message: Message):
    await message.answer(random.choice(msg.COMPLIMENTS))


# /days
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


# /hug
@dp.message(Command("hug"))
@dp.message(F.text == "🤗 Обнимашка")
async def cmd_hug(message: Message):
    await message.answer(msg.HUG_TEXT)
    # уведомление тебе
    try:
        await bot.send_message(
            YOUR_ID,
            f"🤗 Она отправила тебе ОБНИМАШКУ!\n\nОбними её в ответ ❤️"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")


# /miss
@dp.message(Command("miss"))
@dp.message(F.text == "💭 Скучаю")
async def cmd_miss(message: Message):
    await message.answer(msg.MISS_TEXT)
    try:
        await bot.send_message(YOUR_ID, "💭 Она СКУЧАЕТ по тебе! Напиши ей прямо сейчас ❤️")
    except Exception as e:
        print(f"Ошибка: {e}")


# /song
@dp.message(Command("song"))
@dp.message(F.text == "🎵 Песня дня")
async def cmd_song(message: Message):
    await message.answer(random.choice(msg.SONGS))


# /date
@dp.message(Command("date"))
@dp.message(F.text == "💌 Свидание")
async def cmd_date(message: Message):
    await message.answer("💌 Идея для свидания:\n\n" + random.choice(msg.DATES))


# /recipe
@dp.message(Command("recipe"))
@dp.message(F.text == "🍷 Рецепт")
async def cmd_recipe(message: Message):
    await message.answer("🍷 Идея для вечера:\n\n" + random.choice(msg.RECIPES))


# /memory
@dp.message(Command("memory"))
@dp.message(F.text == "📸 Воспоминание")
async def cmd_memory(message: Message):
    await message.answer(random.choice(msg.MEMORIES))


# /countdown
@dp.message(Command("countdown"))
@dp.message(F.text == "⏰ До вечера")
async def cmd_countdown(message: Message):
    left = days_to_event()
    text = f"🍷 До нашего романтического вечера осталось:\n\n<b>{left}</b>\n\nГотовься, будет волшебно 💕"
    await message.answer(text, parse_mode=ParseMode.HTML)


# /quiz — простая викторина
@dp.message(Command("quiz"))
@dp.message(F.text == "🎯 Викторина")
async def cmd_quiz(message: Message):
    q = random.choice(msg.QUIZ_QUESTIONS)
    text = f"🎯 <b>{q['q']}</b>\n\n"
    for i, a in enumerate(q["a"], 1):
        text += f"{i}. {a}\n"
    text += f"\nПравильный ответ: <b>{q['correct']}</b>"
    await message.answer(text, parse_mode=ParseMode.HTML)


# /id — узнать свой ID
@dp.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(f"Твой ID: <code>{message.from_user.id}</code>", parse_mode=ParseMode.HTML)


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

        # сброс счётчиков в новый день
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


async def main():
    # запускаем рассылку параллельно
    asyncio.create_task(send_daily())
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())