import uuid
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, LabeledPrice
from config import PLANS, PAYMENT_PROVIDER_TOKEN, CHANNEL_INVITE_LINK
from db import create_order, get_order_by_payload, mark_order_paid, add_subscription
from keyboards import main_menu

router = Router()

@router.callback_query(F.data.startswith("buy:"))
async def buy(cb: CallbackQuery):
    code = cb.data.split(":", 1)[1]
    if code not in PLANS:
        await cb.answer("Неизвестный тариф", show_alert=True)
        return
    plan = PLANS[code]
    payload = f"{cb.from_user.id}:{code}:{uuid.uuid4().hex[:8]}"
    await create_order(cb.from_user.id, code, plan["price"], plan["currency"], payload)

    if not PAYMENT_PROVIDER_TOKEN:
        await cb.message.answer(
            "Оплата временно недоступна. Свяжитесь с администратором."
        )
        await cb.answer()
        return

    await cb.message.answer_invoice(
        title=f"Подписка {plan['title']}",
        description=f"Доступ на {plan['days']} дней",
        payload=payload,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=plan["currency"],
        prices=[LabeledPrice(label=plan["title"], amount=plan["price"])],
        start_parameter="sub",
    )
    await cb.answer()

@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    order = await get_order_by_payload(q.invoice_payload)
    if not order or order[5] != "pending":
        await q.answer(ok=False, error_message="Заказ не найден или уже оплачен.")
        return
    await q.answer(ok=True)

@router.message(F.successful_payment)
async def on_paid(message: Message):
    payload = message.successful_payment.invoice_payload
    order = await get_order_by_payload(payload)
    if not order:
        await message.answer("Заказ не найден.")
        return
    if order[5] == "paid":
        await message.answer("Этот заказ уже был оплачен.")
        return
    await mark_order_paid(payload)
    plan_code = order[2]
    expires = await add_subscription(order[1], plan_code, PLANS[plan_code]["days"])

    text = (
        f"✅ Оплата получена!\n"
        f"Подписка активна до {expires.strftime('%d.%m.%Y')}."
    )
    if CHANNEL_INVITE_LINK:
        text += f"\n\nСсылка на закрытый канал: {CHANNEL_INVITE_LINK}"

    await message.answer(text, reply_markup=main_menu())
