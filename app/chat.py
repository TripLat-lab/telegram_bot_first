from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from cachetools import TTLCache

router = Router()
ADMIN_ID = 1141265575
BUH_ID = 1141265575

# Раздельные кеши для разных поддержек
admin_chats = TTLCache(maxsize=1000, ttl=86400)
buh_chats = TTLCache(maxsize=1000, ttl=86400)

class SupportStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_buh_message = State()


@router.callback_query(F.data == "buh")
async def start_buh_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Напишите сообщение. Я его перешлю.")
    await state.set_state(SupportStates.waiting_for_buh_message)
    await callback.answer()

@router.message(SupportStates.waiting_for_buh_message, F.chat.type == "private")
async def handle_buh_message(message: Message, state: FSMContext):
    try:
        buh_msg = await message.forward(BUH_ID)
        buh_chats[buh_msg.message_id] = message.from_user.id
        await message.answer("Ваше сообщение отправлено.")
    except TelegramBadRequest:
        await message.answer("Ошибка при отправке. Попробуйте позже.")
    finally:
        await state.clear()


@router.callback_query(F.data == "support")
async def start_admin_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Напишите сообщение. Я его перешлю.")
    await state.set_state(SupportStates.waiting_for_message)
    await callback.answer()

@router.message(F.text == "Задать вопрос")
async def start_support(message: Message, state: FSMContext):
    await message.answer(
        "Напишите сообщение. Я его перешлю.")
    await state.set_state(SupportStates.waiting_for_message)

@router.message(SupportStates.waiting_for_message, F.chat.type == "private")
async def handle_admin_message(message: Message, state: FSMContext):
    try:
        admin_msg = await message.forward(ADMIN_ID)
        admin_chats[admin_msg.message_id] = message.from_user.id
        await message.answer("Ваше сообщение отправлено.")
    except TelegramBadRequest:
        await message.answer("Ошибка при отправке. Попробуйте позже.")
    finally:
        await state.clear()

# Обработчик ответов бухгалтера
@router.message(F.chat.type == "private", F.from_user.id == BUH_ID, F.reply_to_message)
async def buh_reply(message: Message):
    replied_msg = message.reply_to_message
    
    if replied_msg.message_id in buh_chats:
        user_id = buh_chats[replied_msg.message_id]
        try:
            await message.copy_to(user_id)
            await message.answer("Ответ отправлен пользователю")
        except TelegramBadRequest:
            await message.answer("Не удалось отправить (пользователь заблокировал бота)")
    else:
        await message.answer("Диалог устарел или не найден")
@router.message(F.chat.type == "private", F.from_user.id == ADMIN_ID, F.reply_to_message)
async def admin_reply(message: Message):
    replied_msg = message.reply_to_message
    
    if replied_msg.message_id in admin_chats:
        user_id = admin_chats[replied_msg.message_id]
        try:
            await message.copy_to(user_id)
            await message.answer("Ответ отправлен пользователю")
        except TelegramBadRequest:
            await message.answer("Не удалось отправить (пользователь заблокировал бота)")
    else:
        await message.answer("Диалог устарел или не найден")