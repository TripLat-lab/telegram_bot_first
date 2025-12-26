from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from cachetools import TTLCache
from datetime import datetime, timedelta
import app.keyboard.start_kb as kb


router = Router()

SUPPORT_TIMEOUT = timedelta(minutes=5)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

ADMIN_ID = 5792104302
BUH_ID = 5792104302

admin_chats = TTLCache(maxsize=1000, ttl=86400)
buh_chats = TTLCache(maxsize=1000, ttl=86400)

class SupportStates(StatesGroup):
    waiting_for_message = State()


router = Router()

async def start_support_flow(
    *,
    message: Message | CallbackQuery,
    state: FSMContext,
    target_id: int,
    chats_cache: TTLCache
):
    await state.update_data(
        start_time=datetime.utcnow(),
        target_id=target_id,
        chats_cache=chats_cache
    )

    if isinstance(message, CallbackQuery):
        await message.message.answer(
            "Напишите сообщение. Я его перешлю.",
            reply_markup=cancel_kb
        )
        await message.answer()
    else:
        await message.answer(
            "Напишите сообщение. Я его перешлю.",
            reply_markup=cancel_kb
        )

    await state.set_state(SupportStates.waiting_for_message)


@router.callback_query(F.data == "support")
async def start_admin_support(callback: CallbackQuery, state: FSMContext):
    await start_support_flow(
        message=callback,
        state=state,
        target_id=ADMIN_ID,
        chats_cache=admin_chats
    )


@router.callback_query(F.data == "buh")
async def start_buh_support(callback: CallbackQuery, state: FSMContext):
    await start_support_flow(
        message=callback,
        state=state,
        target_id=BUH_ID,
        chats_cache=buh_chats
    )


@router.message(F.text == "Задать вопрос")
async def start_support_from_text(message: Message, state: FSMContext):
    await start_support_flow(
        message=message,
        state=state,
        target_id=ADMIN_ID,
        chats_cache=admin_chats
    )



@router.message(
    SupportStates.waiting_for_message,
    F.text == "Отмена"
)
async def cancel_support(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Диалог отменён.",
        reply_markup=kb.Menu_user
    )



@router.message(SupportStates.waiting_for_message, F.chat.type == "private")
async def handle_support_message(message: Message, state: FSMContext):
    data = await state.get_data()

    start_time: datetime = data.get("start_time")
    target_id: int = data.get("target_id")
    chats_cache: TTLCache = data.get("chats_cache")

    # ⏱ Таймаут
    if not start_time or datetime.utcnow() - start_time > SUPPORT_TIMEOUT:
        await state.clear()
        await message.answer(
            "⏱ Время ожидания истекло.",
            reply_markup=kb.Menu_user
        )
        return

    # 🚫 Игнорируем меню
    menu_items = (
        'Первый рабочий день',
        'Документы и бланки',
        'Отзывы и предложения',
        'Общая информация',
        'Задать вопрос'
    )

    if message.text in menu_items:
        return

    try:
        forwarded = await message.forward(target_id)
        chats_cache[forwarded.message_id] = message.from_user.id

        await message.answer(
            "Ваше сообщение отправлено.",
            reply_markup=kb.Menu_user
        )

    except TelegramBadRequest:
        await message.answer(
            "Ошибка при отправке. Попробуйте позже.",
            reply_markup=kb.Menu_user
        )
    finally:
        await state.clear()



@router.message(F.chat.type == "private", F.reply_to_message)
async def support_reply(message: Message):
    replied_id = message.reply_to_message.message_id

    chats_cache = None
    if message.from_user.id == ADMIN_ID:
        chats_cache = admin_chats
    elif message.from_user.id == BUH_ID:
        chats_cache = buh_chats
    else:
        return

    if replied_id not in chats_cache:
        await message.answer("Диалог устарел или не найден")
        return

    user_id = chats_cache[replied_id]

    try:
        await message.copy_to(user_id)
        await message.answer("Ответ отправлен пользователю")
    except TelegramBadRequest:
        await message.answer("Пользователь заблокировал бота")
