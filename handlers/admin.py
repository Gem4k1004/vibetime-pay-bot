from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS, PLANS
from db import stats, add_subscription

router = Router()

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

@router.message(Command("admin"))
async def admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    s = await stats()
    await message.answer(
        f"📊 Статистика:\n"
        f"Пользователей: {s['users']}\n"
        f"Оплаченных заказов: {s['paid_orders']}\n"
        f"Выручка: {s['revenue']/100:.2f} ₽\n"
        f"Активных подписок: {s['active_subs']}\n\n"
        f"Команды:\n"
        f"/grant <user_id> <plan_code> — выдать подписку\n"
        f"/plans — список тарифов"
    )

@router.message(Command("plans"))
async def plans(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = "\n".join(f"{c}: {p['title']} — {p['price']/100:.0f} {p['currency']}" for c, p in PLANS.items())
    await message.answer(text)

@router.message(Command("grant"))
async def grant(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /grant <user_id> <plan_code>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("user_id должен быть числом.")
        return
    code = parts[2]
    if code not in PLANS:
        await message.answer("Неизвестный тариф.")
        return
    expires = await add_subscription(uid, code, PLANS[code]["days"])
    await message.answer(f"Выдано user {uid}: {code}, до {expires.strftime('%d.%m.%Y')}")
