import os

# ============================================================
# НАСТРОЙКИ БОТА
# ============================================================

# 🔑 Токен от @BotFather
BOT_TOKEN = "8813946651:AAESyWudhb919ff31FZiBtI0Ohs9TkEZ5EI"

# 👤 Твой Telegram ID (узнать можно у @userinfobot)
YOUR_ID = 7823802800

# 💕 ID твоей девушки (она напишет боту /start — ID появится в логах)
HER_ID = 5724121519

# 📅 Дата начала отношений (год, месяц, день, час, мин)
START_DATE = "2026-04-14 03:23"

# 🍷 Дата романтического вечера (когда она выберет — впиши сюда)
DATE_EVENT = "2026-10-01 20:00"

# ⏰ Время уведомлений (по часовому поясу сервера)
MORNING_TIME = "09:00"
DAY_COMPLIMENT_TIME = "12:00"
NIGHT_TIME = "22:00"

# 📁 Путь к БД
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data.json")