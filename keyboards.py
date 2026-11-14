from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PLANS

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Тарифы", callback_data="shop")],
        [InlineKeyboardButton(text="👤 Моя подписка", callback_data="my_sub")],
    ])

def plans_kb():
    rows = []
    for code, p in PLANS.items():
        rows.append([InlineKeyboardButton(
            text=f"{p['title']} — {p['price']/100:.0f} {p['currency']}",
            callback_data=f"buy:{code}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
