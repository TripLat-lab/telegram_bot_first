from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

inline_start_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_menu")]])

start_kb = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text='Давай знакомиться', callback_data='register'),    
InlineKeyboardButton(text='Мы уже знакомы', callback_data='entrance' )],  
[InlineKeyboardButton(text='Написать нам', callback_data='support')]
])

Menu_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Первый рабочий день')], [KeyboardButton(text='Общая информация')],
    [KeyboardButton(text='Документы и бланки')], [KeyboardButton(text='Задать вопрос'),
    KeyboardButton(text="Отзывы и предложения")]],
resize_keyboard=True,
input_field_placeholder='Выберите действие')

get_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить", request_contact=True)]],
    resize_keyboard=True,
    input_field_placeholder='Отправить свой номер телефона'
)

def get_list_organization_self(organization, prefix = 'organizations'):
    builder = InlineKeyboardBuilder()
    for organizations in organization:
        organization_name = organizations.organization_name
        builder.button(
            text=organization_name,
            callback_data=f"{prefix}|{organizations.id}"
        )
    builder.button(text="Назад", callback_data="back_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_list_department_self(department, prefix = 'departments'):
    builder = InlineKeyboardBuilder()
    for departments in department:
        department_name = departments.department_name
        builder.button(
            text=department_name,
            callback_data=f"{prefix}|{departments.id}"
        )
    builder.adjust(2)
    builder.button(text="Назад", callback_data="back_menu")
    return builder.as_markup()