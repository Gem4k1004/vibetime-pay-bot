from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from db import upsert_user
from keyboards import main_menu

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Это Vibetime Pay — магазин подписок. Выберите действие:",
        reply_markup=main_menu(),
    )
