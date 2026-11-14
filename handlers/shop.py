from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import plans_kb, main_menu
from db import get_active_subscription

router = Router()

@router.callback_query(F.data == "menu")
async def back_menu(cb: CallbackQuery):
    await cb.message.edit_text("Главное меню:", reply_markup=main_menu())
    await cb.answer()

@router.callback_query(F.data == "shop")
async def shop(cb: CallbackQuery):
    await cb.message.edit_text("Выберите тариф:", reply_markup=plans_kb())
    await cb.answer()

@router.callback_query(F.data == "my_sub")
async def my_sub(cb: CallbackQuery):
    row = await get_active_subscription(cb.from_user.id)
    if not row:
        text = "У вас нет активной подписки."
    else:
        expires = datetime.fromisoformat(row[4])
        if expires < datetime.utcnow():
            text = "Подписка истекла. Продлите в разделе «Тарифы»."
        else:
            text = f"✅ Активна до: {expires.strftime('%d.%m.%Y %H:%M')} UTC"
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()
