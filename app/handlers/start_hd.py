from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
import logging
import re

import app.keyboard.admin_kb as kb_admin
import app.keyboard.start_kb as kb_start
import app.state.start_st as st
import app.request.start_rq as rq_start
import app.request.registered_rq as rq_reg

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == 'back_menu')
async def back_user(callback: CallbackQuery):
    await callback.message.answer('Выберете действие:',reply_markup=kb_start.start_kb)
    
@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('👋 Привет! Добро пожаловать в команду группы компаний "ПМК". '
            '<b>Давай знакомиться, меня зовут Ботёк 🥸.</b> '
            'Я твой личный гид по нашей компании.\n\n'
            'Как отец, который готов быть рядом, подсказать, направить и '
            'уберечь от ненужных "шишек", так и Ботёк призван стать вашим '
            'надёжным цифровым наставником в этом дивном '
            'новом корпоративном мире.',
              reply_markup=kb_start.start_kb, parse_mode='HTML')

@router.callback_query(F.data == 'entrance')
async def entrance_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'Введите свой номер телефона\nВ формате: +71112223344', 
        reply_markup=kb_start.get_number)
    await state.set_state(st.users.number)
    await callback.answer()
@router.message(st.users.number)
async def auth(message: Message, state: FSMContext):
    number = None
    if message.text:
        number = message.text
    elif message.contact:
        number = message.contact.phone_number
    if number is None:
        await message.answer(f"Вы ввели {number}\nПожалуйста, отправьте номер телефона в формате +71112223344 или через кнопку 'Отправить контакт'.")
        return
    number = re.sub(r"[^\d+]", "", number.strip())
    valid, normalized_number = st.validate_and_normalize_number(number)
    if not valid:
        await message.answer(f"Вы ввели {number}\nНедопустимый формат номера телефона.\nВведите номер в формате +71112223344 или 81112223333")
        return
    if await rq_start.check_number(normalized_number):
        await state.update_data(number=normalized_number)
        await state.set_state(st.users.CHECK)
        name = await rq_start.get_name_user(normalized_number)
        await message.answer(
f'Привет, {name}! Считай меня своим надёжным наставником. Очень рад, что ты с нами! '
f'Моя задача — помочь тебе освоиться. Я введу тебя в курс дела, подскажу, как быстро оформить все документы, и буду твоим "ответом на всё" в любой непонятной ситуации. '
f'Какой вопрос у тебя сейчас самый главный?', 
            reply_markup=kb_start.Menu_user)
        await state.update_data(CHECK=normalized_number)
        await state.set_state(st.upload_link_files_sample.CHECK)
        await state.clear()
    else:
        await message.answer("Номер телефона не найден")

@router.callback_query(F.data == 'register')
async def register_user(callback: CallbackQuery):
    organizations = await rq_reg.get_all_organization()
    if not organizations:
        await callback.answer("Нет доступных организаций")
        return
    await callback.message.answer("Выберите организацию!", reply_markup=kb_start.get_list_organization_self(organizations))
@router.callback_query(F.data.startswith("organizations"))
async def select_organizations_for_user(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой организации не существует!", show_alert=True)
        return
    org = int(parts[1])
    departments = await rq_reg.get_all_department(org)
    if not departments:
        await callback.answer("Нет доступных организаций")
        return
    await state.update_data(department=departments)
    await state.set_state(st.registered_user.department_id)
    dept = await rq_reg.get_all_department(org)
    if not dept:
        await callback.answer()
        return
    await callback.message.answer('Выберите отдел', reply_markup=kb_admin.get_list_department(dept))


@router.message(F.text == 'Отзывы и предложения')
async def comment_and_offers(message: Message):
    await message.answer(f'<a href="https://docs.google.com/forms/d/1avpbd03GGUluS6P_oDYgXB7xhqtcXoSvYMuVKlwY4ZE/edit">заполнить форму</a>', parse_mode="HTML", disable_web_page_preview=True)