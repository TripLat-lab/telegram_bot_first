from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

inline_next_key_one = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_one")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_two = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_two|next_three")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_three = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_three")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_four = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_four")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_five = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_five")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_six = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_six")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_seven = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_seven")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_eight = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_eight")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)

inline_next_key_nine = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="next_nine")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)


inline_next_key_final = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все понятно, готов к дальнейшим шагам", callback_data="final")],
        [InlineKeyboardButton(text="Связаться с HR", callback_data="support")]
    ]
)


def regulations_all(regulations, prefix = 'regulation'):
    builder = InlineKeyboardBuilder()
    for regulation in regulations:
        regulation_name = regulation.type
        builder.button(
            text=regulation_name, callback_data=f'{prefix}|{regulation.id}'
        )
    builder.adjust(1)
    builder.button(text='Все понятно, готов к дальнейшим шагам', callback_data='next_eight')
    builder.button(text='Назад', callback_data='next_six')
    builder.adjust(1)
    return builder.as_markup()

def regulations_all_info(regulations, prefix = 'regulation_info'):
    builder = InlineKeyboardBuilder()
    for regulation in regulations:
        regulation_name = regulation.type
        builder.button(
            text=regulation_name, callback_data=f'{prefix}|{regulation.id}'
        )
    builder.adjust(1)
    builder.button(text='Все понятно, готов к дальнейшим шагам', callback_data='next_eight')
    builder.button(text='Назад', callback_data='back_total_info')
    builder.adjust(1)
    return builder.as_markup()

