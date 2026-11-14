import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
CHANNEL_INVITE_LINK = os.getenv("CHANNEL_INVITE_LINK", "")
DB_PATH = os.getenv("DB_PATH", "shop.db")

PLANS = {
    "m1":  {"title": "1 месяц",    "days": 30,  "price": 30000,  "currency": "RUB"},
    "m3":  {"title": "3 месяца",   "days": 90,  "price": 80000,  "currency": "RUB"},
    "m12": {"title": "12 месяцев", "days": 365, "price": 280000, "currency": "RUB"},
}
