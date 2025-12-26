from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


Menu_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Администрация пользователей и организаций')],
    [KeyboardButton(text='Администрирование файлов')]],
resize_keyboard=True,
input_field_placeholder='Выберите действие')

back_menu_admin = InlineKeyboardMarkup (inline_keyboard=[
[InlineKeyboardButton(text='Отмена', callback_data='back_menu_admin')]])

inline_admin_users = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text='Добавить отдел в приватный режим', callback_data='add_private')],
[InlineKeyboardButton(text='Добавить руководителя или наставника', callback_data='add_boss')],
[InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user'),    
InlineKeyboardButton(text='Добавить отдел', callback_data='add_department' )],  
[InlineKeyboardButton(text='Добавить организацию', callback_data='add_organization'), 
 InlineKeyboardButton(text='Добавить администратора', callback_data='add_admin')]
 ])

inline_reg_organization = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes_organization")],
        [InlineKeyboardButton(text="Нет", callback_data="no_organization")]])

inline_reg_admin_new = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes_admin")],
        [InlineKeyboardButton(text="Нет", callback_data="no_admin")]])

inline_reg_department = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes_department")],
        [InlineKeyboardButton(text="Нет", callback_data="no_department")]])

inline_reg_users = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes_users")],
        [InlineKeyboardButton(text="Нет", callback_data="no_users")]])

inline_reg_user_back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_menu")]])

inline_boss_or_mentor = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Руководитель", callback_data="yes_mentor")],
        [InlineKeyboardButton(text="Наставник", callback_data="no_mentor")]])

yes_or_no_boss = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes_boss'),
    InlineKeyboardButton(text='Нет', callback_data='no_boss')]
])

def get_list_organization(organization, prefix = 'org'):
    builder = InlineKeyboardBuilder()
    for org in organization:
        organization_name = org.organization_name
        builder.button(
            text=organization_name,
            callback_data=f"{prefix}|{org.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()

def get_list_department(department, prefix = 'dept'):
    builder = InlineKeyboardBuilder()
    for dept in department:
        department_name = dept.department_name
        builder.button(
            text=department_name,
            callback_data=f"{prefix}|{dept.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()

def get_list_organization_for_user(organization, prefix = 'org_user'):
    builder = InlineKeyboardBuilder()
    for org_user in organization:
        organization_name = org_user.organization_name
        builder.button(
            text=organization_name,
            callback_data=f"{prefix}|{org_user.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()

def get_list_boss_organization(organization, prefix = 'get_org'):
    builder = InlineKeyboardBuilder()
    for get_org in organization:
        organization_name = get_org.organization_name
        builder.button(
            text=organization_name,
            callback_data=f"{prefix}|{get_org.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()

def get_list_users(users, prefix = 'user'):
    builder = InlineKeyboardBuilder()
    for user in users:
        name = user.name
        builder.button(
            text=name, callback_data=f'{prefix}|{user.id}'
        ) 
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()

def get_list_department_boss(department, prefix = 'dep'):
    builder = InlineKeyboardBuilder()
    for dep in department:
        department_name = dep.department_name
        builder.button(
            text=department_name,
            callback_data=f"{prefix}|{dep.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_users")
    return builder.as_markup()