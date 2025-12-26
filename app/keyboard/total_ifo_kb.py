from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)


inline_total_menu_private = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Мотивация', callback_data='motivation')],
        [InlineKeyboardButton(text='Наши направления', callback_data='directions'),
         InlineKeyboardButton(text='Филиалы', callback_data='branches')],
        [InlineKeyboardButton(text='Бонусы', callback_data='bonus'),
        InlineKeyboardButton(text='Порядок трудоустройства', callback_data='employment')],
        [InlineKeyboardButton(text='Регламенты', callback_data='next_seven'),
        InlineKeyboardButton(text='Welcome Book', callback_data='welcome')]
        ])


inline_total_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Наши направления', callback_data='directions'),
         InlineKeyboardButton(text='Филиалы', callback_data='branches')],
        [InlineKeyboardButton(text='Бонусы', callback_data='bonus'),
        InlineKeyboardButton(text='Порядок трудоустройства', callback_data='employment')],
        [InlineKeyboardButton(text='Регламенты', callback_data='next_seven'),
        InlineKeyboardButton(text='Welcome Book', callback_data='welcome')],
        ])

inline_info_branches = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='С?М Магазин', callback_data='SM_store'),
         InlineKeyboardButton(text='Головной офис', callback_data='total_office')],
         [InlineKeyboardButton(text='Строительное направление', callback_data='construction'),
          InlineKeyboardButton(text='Завод', callback_data='factory')],
          [InlineKeyboardButton(text='Назад', callback_data='back_total_info')]
])

inline_back_info_pmk = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='офис', callback_data='total_office'),
    InlineKeyboardButton(text='Производство', callback_data='factory')],
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info')]
])

inline_back_info_gk_pmk = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info'),
    InlineKeyboardButton(text='Навигация', callback_data='total_office')]
])

inline_back_info_builder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info'),
    InlineKeyboardButton(text='Навигация', callback_data='builder_navigation')]
])

inline_back_info_shop = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info'),
    InlineKeyboardButton(text='Навигация', callback_data='SM_store')]
])

inline_back_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info'),
    InlineKeyboardButton(text='Связаться с HR', callback_data='support')]
])

inline_back_info_bonus = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info'),
    InlineKeyboardButton(text='Связаться с HR', callback_data='support')]
])

inline_info_directions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Завод металлоконструкций «ПМК»', callback_data='pmk')],
    [InlineKeyboardButton(text='Cтроительство полного цикла ГК «ПМК»', callback_data='gk_pmk')],
    [InlineKeyboardButton(text='Проектное бюро «Team Trade»', callback_data='tt')],
    [InlineKeyboardButton(text='ЧОП «ХАНГАР»', callback_data='defender')],
    [InlineKeyboardButton(text='Бренд одежды «Сколько? Можно»', callback_data='shop')],
    [InlineKeyboardButton(text='Сельское хозяйство КФХ Вороново', callback_data='farm')],
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info')]
])

inline_info_bonus = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ДМС', callback_data='dms')],
    [InlineKeyboardButton(text='Корпоративный фитнес', callback_data='fitness')],
    [InlineKeyboardButton(text='Компенсации', callback_data='compensation')],
    [InlineKeyboardButton(text='Реферальная программа', callback_data='referral')],
    [InlineKeyboardButton(text='Корпоративное питание', callback_data='food')],
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info')]
])

inline_employment_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Производство', callback_data='manufacture')],
    [InlineKeyboardButton(text='Офис', callback_data='office_job')],
    [InlineKeyboardButton(text='Вахта', callback_data='vahta')],
    [InlineKeyboardButton(text='Назад', callback_data='back_total_info')]
])


