from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router, types, Bot
from aiogram.fsm.context import FSMContext
import logging

import app.keyboard.start_kb as kb_user
import app.keyboard.admin_kb as kb_admin
import app.keyboard.file.sample_kb as kb_sample
import app.state.start_st as st
import app.request.start_rq as rq_start
import app.request.registered_rq as rq_reg

import re


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "Назад")
async def back_menu_admin(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите действие", reply_markup=kb_admin.back_menu_admin
    )


@router.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext):
    await rq_reg.default_org()
    await rq_start.init_admin_data()
    telegram_id = message.from_user.id
    user_exists = await rq_reg.check_is_admin(telegram_id)
    if not user_exists:
        await message.answer(" У вас нет прав для выполнения этой команды")
        return
    await message.answer("Введите новый пароль")
    await state.set_state(st.admin.reg_password)


@router.message(st.admin.reg_password)
async def register_admin(message: Message, state: FSMContext):
    register_admin = message.text
    telegram_id = message.from_user.id
    await rq_start.reg_adm(register_admin, telegram_id)
    await message.answer("Регистрация прошла успешно!")
    await state.clear() 


async def clear_state_safely(state: FSMContext):
    try:
        await state.clear()
    except Exception as e:
        logger.error(f"Error clearing state: {e}", exc_info=True)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await message.answer(" У вас нет прав для выполнения этой команды")
        return
    await message.answer(f"Введите пароль")
    await state.set_state(st.admin.password)


@router.message(st.admin.password)
async def authorization(message: Message, state: FSMContext):

    password = message.text
    if await rq_start.check_password(password):
        await message.answer("Добро пожаловать!", reply_markup=kb_admin.Menu_admin)
    else:
        await message.answer("Вход запрещен!")
    await state.clear() 


async def clear_state_safely(state: FSMContext):
    try:
        await state.clear()
    except Exception as e:
        logger.error(f"Error clearing state: {e}", exc_info=True)


@router.message(F.text == "Администрация пользователей и организаций")
async def start_admin(message: Message):
    await message.answer("Выберете действие:", reply_markup=kb_admin.inline_admin_users)


@router.callback_query(F.data == "back_users")
async def back_user(callback: CallbackQuery):
    await callback.message.answer(
        "Выберете действие:", reply_markup=kb_admin.inline_admin_users
    )


@router.callback_query(F.data == "add_admin")
async def add_admin(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    await callback.message.answer("Укажите телеграмм id нового администратора")
    await state.set_state(st.admin.reg_id)


@router.message(st.admin.reg_id)
async def add_new_pin_admin(message: Message, state: FSMContext):
    await state.update_data(reg_id=message.text)
    await message.answer("Укажите пароль для нового администратора")
    await state.set_state(st.admin.reg_pin)


@router.message(st.admin.reg_pin)
async def register_new_admin(message: Message, state: FSMContext):
    await state.update_data(reg_pin=message.text)
    data = await state.get_data()
    new_pin = data.get("reg_pin")
    new_telegram_id = data.get("reg_id")
    await message.answer(
        f"Подтвердите данные"
        f"\nПароль: {new_pin}"
        f"\nТелеграмм id: {new_telegram_id}",
        reply_markup=kb_admin.inline_reg_admin_new,
    )


@router.callback_query(F.data.in_(["yes_admin", "no_admin"]))
async def save_new_admin(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes_admin":
        data = await state.get_data()
        new_pin = data.get("reg_pin")
        new_telegram_id = data.get("reg_id")
        if not all([new_telegram_id, new_pin]):
            await callback.message.edit_text(
                "Ошибка: не хватает данных для добавления пользователя."
            )
            await state.clear() 
            return
        await rq_reg.reg_new_admin(new_telegram_id, new_pin)
        await callback.message.answer(
            f"Администратор добавлен!", reply_markup=kb_admin.Menu_admin
        )
    else:
        await callback.message.edit_text(
            "Отменено", reply_markup=kb_admin.inline_admin_users
        )
    await state.clear() 


@router.callback_query(F.data == "add_organization")
async def add_organization(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите название организации", reply_markup=kb_admin.inline_reg_user_back
    )
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    await state.set_state(st.registered_department.organization)
    await callback.answer()


@router.message(st.registered_department.organization)
async def register_organization(message: Message, state: FSMContext):
    await state.update_data(organization_name=message.text)
    await message.answer(
        f"Добавить организацию: {message.text}",
        reply_markup=kb_admin.inline_reg_organization,
    )


@router.callback_query(F.data.in_(["yes_organization", "no_organization"]))
async def save_organization(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes_organization":
        data = await state.get_data()
        if await rq_reg.reg_organization(data["organization_name"]):
            await callback.message.edit_text(
                f"Организация: {data['organization_name']} Добавлена!"
            )
        else:
            await callback.message.edit_text("Ошибка добавления!")
    else:
        await callback.message.edit_text(
            "Отменено", reply_markup=kb_admin.inline_admin_users
        )
    await state.clear() 


@router.callback_query(F.data == "add_department")
async def add_department(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    org = await rq_reg.get_all_organization()
    if not org:
        await callback.answer("Нет доступных организаций")
        return
    await callback.message.answer(
        "Выберите в какую организацию добавить отдел!",
        reply_markup=kb_admin.get_list_organization(org),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("org|"))
async def select_organization(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой организации не существует!", show_alert=True)
        return
    organization_id = int(parts[1])
    await state.update_data(organization_id=organization_id)
    await state.set_state(st.registered_department.get_organization)
    await callback.answer()
    await callback.message.answer(
        "Введите название отдела", reply_markup=kb_admin.inline_reg_user_back
    )


@router.message(st.registered_department.get_organization)
async def input_department_name(message: Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(st.registered_department.department)
    await message.answer(
        f"Вы ввели отдел: {message.text}. Подтвердите создание.",
        reply_markup=kb_admin.inline_reg_department,
    )


@router.callback_query(F.data.in_(["yes_department", "no_department"]))
async def save_department(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes_department":
        data = await state.get_data()
        department_name = data.get("department")
        organization_id = data.get("organization_id")
        if department_name is None:
            await callback.message.edit_text(
                "Ошибка: название отдела не найдено в состоянии."
            )
            await state.clear() 
            return
        successful = await rq_reg.reg_department(department_name, organization_id)
        if successful:
            await callback.message.edit_text(f"Отдел: {department_name} \nДобавлена!")
        else:
            await callback.message.edit_text("Ошибка добавления!")
    else:
        await callback.message.edit_text(
            "Отменено", reply_markup=kb_admin.inline_admin_users
        )
    await state.clear() 


@router.callback_query(F.data == "add_user")
async def select_user_org(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    org_user = await rq_reg.get_all_organization()
    await callback.message.answer(
        "Вы берите организацию из списка",
        reply_markup=kb_admin.get_list_organization_for_user(org_user),
    )


@router.callback_query(F.data.startswith("org_user|"))
async def select_department_user(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой организации не существует!", show_alert=True)
        return
    org = int(parts[1])
    dept = await rq_reg.get_all_department(org)
    if not dept:
        await callback.answer("Нет доступных отделов")
        return
    await callback.message.answer(
        "Выберите доступный отдел!", reply_markup=kb_admin.get_list_department(dept)
    )


@router.callback_query(F.data.startswith("dept"))
async def select_user_department(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такого отдела не существует", show_alert=True)
        return
    department_id = int(parts[1])
    await state.update_data(department_id=department_id)
    await state.set_state(st.registered_user.department_id)
    telegram_id = callback.message.from_user.id
    user_admin = await rq_reg.check_is_admin(telegram_id)
    if not user_admin:
        await callback.message.answer(
            "Введите свой номер телефона\nВ формате: +71112223344",
            reply_markup=kb_user.get_number,
        )
        await state.set_state(st.registered_user.number_user)
        return
    await callback.message.answer(
        f"Введите номер телефона пользователя \nВ формате +71112223344",
        reply_markup=kb_admin.inline_reg_user_back,
    )
    await state.set_state(st.registered_user.number_user)
    await callback.answer()


@router.message(st.registered_user.number_user)
async def auth(message: Message, state: FSMContext):
    number = None
    if message.text:
        number = message.text
    elif message.contact:
        number = message.contact.phone_number
    if number is None:
        await message.answer(
            "Пожалуйста, отправьте номер телефона в формате +71112223344 или через кнопку 'Отправить контакт'.",
            reply_markup=kb_user.inline_start_menu,
        )
        return
    number = re.sub(r"[^\d+]", "", number.strip())
    valid, normalized_number = st.validate_and_normalize_number(number)
    if not valid:
        await message.answer(
            "Недопустимый формат номера телефона.\nВведите номер в формате: +71112223344 или 81112223333",
            reply_markup=kb_user.inline_start_menu,
        )
        return
    await state.update_data(number=normalized_number)
    await state.set_state(st.registered_user.number)
    telegram_id = message.from_user.id
    user_admin = await rq_reg.check_is_admin(telegram_id)
    if not user_admin:
        await message.answer(
            "Введите своё имя", reply_markup=kb_admin.inline_reg_user_back
        )
        return
    await message.answer(
        f"Введите имя нового сотрудник", reply_markup=kb_admin.inline_reg_user_back
    )


@router.message(st.registered_user.number)
async def input_users_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.registered_user.name)
    name = message.text
    if not name or not name.strip():
        await message.answer("Пожалуйста, введите корректное имя.")
        await state.finish()
        return
    data = await state.get_data()
    department_id = data.get("department_id")
    number = data.get("number")
    name = data.get("name")
    department_name = await rq_reg.get_department_name(department_id)
    await message.answer(
        f"Отдел: {department_name}\n"
        f"Номер телефона: {number}\n"
        f"Имя: {name}\n"
        f"Подтвердите создание.",
        reply_markup=kb_admin.inline_reg_users,
    )


@router.callback_query(F.data.in_(["yes_users", "no_users"]))
async def save_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.data == "yes_users":
        data = await state.get_data()
        department_id = data.get("department_id")
        name = data.get("name")
        number = data.get("number") or data.get("number_user")
        if not all([department_id, name, number]):
            await callback.message.edit_text(
                "Ошибка: не хватает данных для добавления пользователя."
            )
            await state.clear() 
            return
        successful = await rq_reg.reg_users(
        department_id=department_id,
        number=number,
        name=name,
        telegram_id=callback.from_user.id,
        bot=bot,
        state=state
        )
        if successful:
            if not successful:
                return await callback.message.answer('Пользователь уже зарегестрирован!')
            telegram_id = callback.from_user.id
            user_admin = await rq_reg.check_is_admin(telegram_id)
            if not user_admin:
                await callback.message.answer(
f'Привет, {name}! Считай меня своим надёжным наставником. Очень рад, что ты с нами!'
f'Моя задача — помочь тебе освоиться. Я введу тебя в курс дела, подскажу, как быстро оформить все документы, и буду твоим "ответом на всё" в любой непонятной ситуации. '
f'<b>Какой вопрос у тебя сейчас самый главный?</b>',
                    reply_markup=kb_user.Menu_user, parse_mode='HTML'
                )
                await state.update_data(CHECK=number)
                await state.finish()
                return
            await callback.message.answer(
                f"Сотрудник: {name} \nДобавлен!", reply_markup=kb_admin.Menu_admin
            )
            await state.finish()
        else:
            await callback.message.edit_text("Пользователь уже зарегестрирован!")
    else:
        await callback.message.edit_text("Отменено", reply_markup=kb_user.start_kb)
        await state.finish()
    await state.clear() 


@router.callback_query(F.data == "add_boss")
async def start_add_boss(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    get_org = await rq_reg.get_all_organization()
    if not get_org:
        await callback.answer("Нет доступных организаций")
        return
    await callback.message.answer(
        "Выберите организацию",
        reply_markup=kb_admin.get_list_boss_organization(get_org),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("get_org"))
async def select_organization_boss(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой организации не существует!", show_alert=True)
        return
    organization_id = int(parts[1])
    await state.update_data(organization_id=organization_id)
    await state.set_state(st.add_boss.organization)
    get_org = organization_id
    dep = await rq_reg.get_all_department(get_org)
    if not dep:
        await callback.message.answer("Нет доступных отделов!")
        return
    await callback.message.answer(
        "Выберите отдел", reply_markup=kb_admin.get_list_department_boss(dep)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dep|"))
async def select_user_boss(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.message.answer("Такого отдела не существует!", show_alert=True)
        return
    department_id = int(parts[1])
    await state.update_data(department_id=department_id)
    await state.set_state(st.add_boss.department)
    dep = department_id
    user = await rq_reg.get_list_users(dep)
    if not user:
        await callback.message.answer("Нет доступных отделов!")
        return
    await callback.message.answer(
        "Выберите пользователя для повышения прав",
        reply_markup=kb_admin.get_list_users(user),
    )


@router.callback_query(F.data.startswith("user|"))
async def get_url_boss(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.message.answer("Такого отдела не существует!", show_alert=True)
        return
    user_id = int(parts[1])
    await state.update_data(user_id=user_id)
    await state.set_state(st.add_boss.user)
    await callback.message.answer(
        f"Введите короткую ссылку на руководителя",
        reply_markup=kb_admin.inline_reg_user_back,
    )
    await state.set_state(st.add_boss.url)
    await callback.answer()
    #!!!!!!!!МОЖЕТ БЫТЬ НУЖНО БУДЕТ ТУТЬ ДОБАВИТЬ ПОЧТУ ПУКОВОДИТЕЛЯ!!!!


@router.message(st.add_boss.url)
async def save_boss(message: Message, state: FSMContext):
    url = message.text
    await state.update_data(url=url)
    await state.set_state(st.add_boss.url)
    await message.answer(
        "Является ли он руководителем отдела",
        reply_markup=kb_admin.inline_boss_or_mentor,
    )


@router.callback_query(F.data.in_(["yes_mentor", "no_mentor"]))
async def mentor_or_boss(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes_mentor":
        data = await state.get_data()
        name_id = data.get("user_id")
        telegram_url = data.get("url")
        department_id = data.get("department_id")
        mentor = "No"
        organization_id = data.get("organization_id")
        telegram = str(telegram_url)
        user = await rq_reg.get_user_name(user_id=name_id, user_number=None, telegram_id=None)
        department = await rq_reg.get_department_name(department_id)
        organization = await rq_reg.get_all_organization_name(organization_id)
        await state.update_data(mentor=mentor)
        await state.set_state(st.add_boss.mentor)
        await callback.message.answer(
            f"Пользователь:{user},\n"
            f"Короткая ссылка: {telegram},\n"
            f"Название отдела: {department},\n"
            f"Является ли наставником: {mentor},\n"
            f"Организация: {organization}"
            "Все верно?",
            reply_markup=kb_admin.yes_or_no_boss,
        )
    else:
        data = await state.get_data()
        name_id = data.get("user_id")
        telegram_url = data.get("url")
        department_id = data.get("department_id")
        organization_id = data.get("organization_id")
        telegram = str(telegram_url)
        user = await rq_reg.get_user_name(user_id=name_id, user_number=None, telegram_id=None)
        department = await rq_reg.get_department_name(department_id)
        organization = await rq_reg.get_all_organization_name(organization_id)
        mentor = department
        await state.update_data(mentor=mentor)
        await state.set_state(st.add_boss.mentor)
        await callback.message.answer(
            f"Пользователь:{user},\n"
            f"Короткая ссылка: {telegram},\n"
            f"Название отдела: {department},\n"
            f"Является ли наставником: {mentor},\n"
            f"Организация: {organization}"
            "Все верно?",
            reply_markup=kb_admin.yes_or_no_boss,
        )


@router.callback_query(F.data.in_(["yes_boss", "no_boss"]))
async def save_boss(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yes_boss":
        data = await state.get_data()
        name_id = data.get("user_id")
        telegram_url = data.get("url")
        department_id = data.get("department_id")
        organization_id = data.get("organization_id")
        mentor = data.get("mentor")
        mentor_or_boss = await rq_reg.reg_mentor_or_boss(
            name_id, telegram_url, department_id, organization_id, mentor
        )
        if mentor_or_boss:
            await callback.message.answer(
                "Добавлено!", reply_markup=kb_admin.Menu_admin
            )
            await state.clear() 
        else:
            await callback.message.answer("ошибка!", reply_markup=kb_admin.Menu_admin)
            await state.clear() 
    else:
        await callback.message.answer("Отменено!", reply_markup=kb_admin.Menu_admin)
    await state.clear() 


@router.callback_query(F.data.in_(["add_private"]))
async def select_priv_org(callback: CallbackQuery):
    org_id = await rq_reg.get_all_organization()
    await callback.message.answer('Выберите организацию',
                                  reply_markup=kb_sample.select_sample_org(organization=org_id, prefix='primate_org'))
@router.callback_query(F.data.startswith(("primate_org"))) 
async def select_user_dept_for_private(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    org_id = int(parts[1])
    dept_id = await rq_reg.get_all_department(org_id)
    await callback.message.answer('Выберите нужны отдел',
                                  reply_markup=kb_sample.select_sample_dept(departments=dept_id, prefix='private_det'))
    await state.update_data(org_id=org_id)

@router.callback_query(F.data.startswith(("private_det"))) 
async def definition_private(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    dept_id = int(parts[1])
    dept_name = await rq_reg.get_department_name(dept_id)
    data = await state.get_data()
    org_id = data.get("org_id")
    org_name = await rq_reg.get_all_organization_name(org_id)
    await state.set_state(st.add_private.private)
    await state.update_data(org_id=org_id, dept_id=dept_id)
    await callback.message.answer ('Вы указали' 
                                   f'\nОрганизация: {dept_name}'
                                   f'\nОтдео: {org_name}'
                                   '\nВсе верно?:',
                                   reply_markup=kb_admin.inline_add_private_dept)
    
@router.callback_query(F.data == 'yes_private')
async def save_private(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dept_id = data.get('dept_id')
    complite = await rq_reg.save_private(dept_id)
    if complite == False:
        await callback.message.answer('Сохранить не получилось обратитесь в поддержку')
        await state.clear()
    await callback.message.answer('Сохранено!')
    await state.clear()