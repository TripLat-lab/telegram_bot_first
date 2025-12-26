from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

inline_add_doc_file = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить приватный файл", callback_data="add_private_files")],
        [InlineKeyboardButton(text="Фотографии", callback_data="photo")],
        [InlineKeyboardButton(text="Образцы заявлений", callback_data="add_sample")],
        [InlineKeyboardButton(text="Положения (ЛНА)", callback_data="add_offers")],
        [InlineKeyboardButton(text="ПДФ", callback_data="add_pdf")],
        [InlineKeyboardButton(text="Видео преведствие", callback_data="add_videos")],
        [InlineKeyboardButton(text='Положения отделов', callback_data='department_offer')],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")],
    ]
)

inline_add_pdf_file = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Информация о ГК", callback_data="GK_PDF"),
            InlineKeyboardButton(
                text="Оргструктура компании", callback_data="company_structure"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Регламенты отделов", callback_data="add_department_pdf"
            ),
            InlineKeyboardButton(text="Процессы", callback_data="process"),
        ],
        [
            InlineKeyboardButton(text="Информация о ДМС", callback_data="dms_info"),
            InlineKeyboardButton(text="Welcome book", callback_data="welcome_book"),
        ],
        [InlineKeyboardButton(text="Информация о компании", callback_data="compony_info")],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")],
    ]
)

inline_add_video_file = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Общие", callback_data="public_videos"),
            InlineKeyboardButton(text="Видео отдела", callback_data="department_videos"),
            InlineKeyboardButton(text="Топ менеджера", callback_data='top_menedment'),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")],
    ]
)


def select_video_org(organization, prefix="org_videos, org_pdf, org_offer"):
    builder = InlineKeyboardBuilder()
    for org_videos in organization:
        organization_name = org_videos.organization_name
        builder.button(
            text=organization_name, callback_data=f"{prefix}|{org_videos.id}"
        )
        builder.adjust(2)
    builder.button(text="Назад", callback_data="back_sample_admin")
    return builder.as_markup()


def select_dept_videos(department, prefix="video_dept, photo_dept, offer_dept"):
    builder = InlineKeyboardBuilder()
    for video_dept in department:
        department_name = video_dept.department_name
        builder.button(text=department_name, callback_data=f"{prefix}|{video_dept.id}")
        builder.adjust(2)
    builder.button(text="Назад", callback_data="back_sample_admin")
    return builder.as_markup()


yes_no_keyboard_video_add = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="ok_video")],
        [InlineKeyboardButton(text="Нет", callback_data="back_sample_admin")],
    ]
)

inline_select_doc_files = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заявление на отпуск", callback_data="add_keyboards_sample_holiday"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление на трудоустройство", callback_data="get_A_job"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление об увольнении", callback_data="out_a_job"
            )
        ],
        [InlineKeyboardButton(text="Служебные записки", callback_data="Internal_memo")],
    ]
)

inline_select_holiday = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заявление на отпуск", callback_data="add_sample_holiday"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление на отпуск за свой счет", callback_data="add_no_money"
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")],
    ]
)

back_menu_sample = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="back_sample_admin")]
    ]
)

def select_sample_dept(departments, prefix=("private", 'private_det')):
    builder = InlineKeyboardBuilder()
    for department in departments:
        department_name = department.department_name
        builder.button(
            text=department_name, callback_data=f"{prefix}|{department.id}"
        )
        builder.adjust(1)
    builder.button(text='Назад', callback_data='back_sample_admin')
    builder.adjust(1)
    return builder.as_markup()


def select_sample_org(organization, prefix=("org_select", "org_photo", 'org_offer', 'org_private',
                                            'primate_org')):
    builder = InlineKeyboardBuilder()
    for org_select in organization:
        organization_name = org_select.organization_name
        builder.button(
            text=organization_name, callback_data=f"{prefix}|{org_select.id}"
        )
        builder.adjust(2)
    builder.button(text="Назад", callback_data="back_sample_admin")
    return builder.as_markup()


inline_add_sample = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="ok_sample")],
        [InlineKeyboardButton(text="Нет", callback_data="no_sample")],
    ]
)

inline_select_doc_files_for_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заявление на отпуск", callback_data="sample_holiday"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление на трудоустройство", callback_data="get_A_job_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление об увольнении", callback_data="out_a_job_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="Служебные записки", callback_data="Internal_memo_user"
            )
        ],
        [InlineKeyboardButton(text="Назад!", callback_data="back_sample_user")],
    ]
)

inline_select_holiday_users = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заявление на отпуск", callback_data="add_sample_holiday_users"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заявление на отпуск за свой счет",
                callback_data="add_no_money_user",
            )
        ],
        [InlineKeyboardButton(text="Назад!", callback_data="back_sample_user")],
    ]
)


def select_sample_for_user(file_type, prefix="select_type_sample_user"):
    builder = InlineKeyboardBuilder()
    for select_type_sample_user in file_type:
        name = select_type_sample_user.name
        builder.button(
            text=name, callback_data=f"{prefix}|{select_type_sample_user.id}"
        )
    builder.adjust(1)
    builder.button(text="Назад", callback_data="back_sample_user")
    builder.adjust(1)
    return builder.as_markup()


inline_offers_and_simple = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Образцы заявлений", callback_data="sample")],
        [InlineKeyboardButton(text="Положения (ЛНА)", callback_data="offers")],
        [InlineKeyboardButton(text="Заказать справку", callback_data="reference")],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_user")],
    ]
)

inline_reference_hr_and_buh = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Кадровые справки", callback_data="support")],
        [InlineKeyboardButton(text="Cправки по доходу", callback_data="buh")],
    ]
)

inline_image = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Орг. структура", callback_data="org")],
        [InlineKeyboardButton(text="Медецинская комиссия", callback_data="medical")],
        [InlineKeyboardButton(text="Общии фото для организации", callback_data="logo")],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")]
    ]
)

inline_image_dept_or_org = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Навигация", callback_data="medical_dept")],
        [InlineKeyboardButton(text="Логотип", callback_data="medical_logo")],
        [InlineKeyboardButton(text="Назад", callback_data="back_sample_admin")],
    ]
)
