from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaDocument
from aiogram import F, Router
import app.request.link_files.sample_link_file_rq as rq_link
from aiogram.fsm.context import FSMContext
import logging
import asyncio

import app.keyboard.total_ifo_kb as kb_info
import app.request.registered_rq as rq_reg




router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == 'back_total_info')
async def back_total_info(callback: CallbackQuery):
    await callback.message.answer('Выберите нужный пункт', reply_markup=kb_info.inline_total_menu)

@router.message(F.text == 'Общая информация')
async def total_info_start(message: Message):
    user_id = message.from_user.id
    is_private = await rq_reg.check_is_private_files(user_id)
    user_number = await rq_reg.get_user_number(user_id)
    dept_id = await rq_reg.get_dept_id(user_number)
    dept_name = await rq_reg.get_department_name(dept_id)

    if is_private:
        await message.answer('Выберите нужный пункт', reply_markup=kb_info.inline_total_menu_private)
        return

    if dept_name == 'Отдел ПТО':
        await message.answer('Выберите нужный пункт', reply_markup=kb_info.inline_total_menu_private_pto)
        return
    if dept_name == 'Коммерческий отдел':
        await message.answer('Выберите нужный пункт', reply_markup=kb_info.inline_total_menu_private)
        return
    else:
        await message.answer('Выберите нужный пункт', reply_markup=kb_info.inline_total_menu)

@router.callback_query(F.data == 'branches')
async def info_branches (callback: CallbackQuery):
    await callback.message.answer('Выберите о каком филиале рассказать', reply_markup=kb_info.inline_info_branches)
@router.callback_query(F.data == 'SM_store')
async def info_SM_store(callback: CallbackQuery, state: FSMContext):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRzA3u\">Красный просп., 49</a>'
    text = (f'Ждём Вас в наш concept store по адресу: {card} ' 
                                  f'\nВход со стороны Красного проспекта.' 
                                  f'\nГрафик работы магазина: с 10:00 до 21:00')
    type_value = 'Навигация'
    organization_id = 5
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")
@router.callback_query(F.data == 'total_office')
async def info_total_office(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRvKIF\">ул. Ядринцевская, 72</a>'
    text = (f'Головной офис компании находится по адресу: ' 
                                  f'\nг. Новосибирск, {card}  8 этаж.'
                                  f'\nВход: со стороны ул.Ядринцевская, под кафе "GeLatte".'
                                  f'\nНа этаж пропускная система, попасть к нам можно только по предварительной договорённости.'
                                  f'\nОфис работает до 18:00, бухгалтерия до 17:00')
    await callback.message.answer(text, reply_markup=kb_info.inline_back_info, parse_mode="HTML", disable_web_page_preview=True)

@router.callback_query(F.data == 'construction')
async def info_construction(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRvKIF\">ул. Ядринцевская, 72</a>'
    link = 'https://www.gc-pmk.ru/'
    await callback.message.answer(f'\nСтроительное направление компании находится по адресу:' 
                                  f'\nг. Новосибирск, {card} 1 этаж.'
                                  f' Вход: со стороны ул.Ядринцевская, под кафе "GeLatte". '
                                  f'\nОфис работает до 18:00. Попасть к нам можно только по предварительной договорённости.',
                                    reply_markup=kb_info.inline_back_info, parse_mode="HTML", disable_web_page_preview=True)
@router.callback_query(F.data == 'factory')
async def info_factory(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRzNkt\">м-н Пашино, ул. Селенгинская, 15</a>'
    text = (f'Наше производство находится по адресу: {card} '
                                  f'\nВход со стороны ул. Стадионной. На производстве действует пропускная система, при себе необходимо иметь паспорт.')
    type_value = 'Навигация'
    organization_id = 1
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")

@router.callback_query(F.data == 'directions')
async def total_directions(callback: CallbackQuery):
    await callback.message.answer(f'Группа компаний «ПМК» – это многопрофильное объединение, включающее в себя несколько специализированных компаний, работающих в различных отраслях. \
                                  \nМы предлагаем широкий спектр услуг, от проектирования и строительства до логистики и производства. \
                                  \nНаша цель – предоставлять комплексные решения для бизнеса и частных лиц, обеспечивая высокое качество и надежность на каждом этапе.', reply_markup=kb_info.inline_info_directions, disable_web_page_preview=True)
@router.callback_query(F.data == 'pmk')
async def pmk_info(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRzNkt\">м-н Пашино, ул. Селенгинская, 15</a>'
    link = 'https://pmk-sib.ru/'
    text = (
        f"{card}\n\n"
        "Описание: Производственное предприятие, работающее на рынке с 2013 года. "
        "Полный цикл работ: проектирование, изготовление, доставка и монтаж металлоконструкций. "
        "Все этапы обеспечиваются собственными ресурсами – от производства до монтажа.\n\n"
        f"Сайт: <a href=\"{link}\">Открыть сайт</a>\n\n"
        "Собственник и Генеральный директор: Иванов Алексей Андреевич\n"
        "Директор по производству: Титаев Павел Сергеевич")
    
    type_value = 'Логотип'
    organization_id = 1
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info_pmk,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")
@router.callback_query(F.data == 'gk_pmk')
async def gk_pmk_info(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRvKIF\">ул. Ядринцевская, 72</a>'
    link = 'https://www.gc-pmk.ru/'
    text = (
        f'{card} \n\n'
        'Описание: Строительство объектов гражданского и промышленного назначения всех уровней сложности' 
        ' (от спортивных сооружений до больниц и заводов) с 2018 года. Реализация проектов "под ключ" – от проектирования и' 
        'монтажа до сервисного обслуживания. \n\n'
        f"Сайт: <a href=\"{link}\">Открыть сайт</a>\n\n"
        'Генеральный директор: Аванесян Михитар Рашидович')
    type_value = 'Логотип'
    organization_id = 1
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info_gk_pmk,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")
@router.callback_query(F.data == 'tt')
async def tt_info(callback: CallbackQuery):
    link = 'https://team-tr.ru/'
    card = '<a href=\"https://yandex.ru/maps/-/CLBRvQzj\">ул. Ядринцевская, 72</a>'
    text = (
        f'{card} \n\n'
        'Oписание: Проектирование объектов гражданского и промышленного назначения, разработка всех разделов проектной'
        'и рабочей документации. Услуги проектирования зданий и комплексов "под ключ", в том числе в сложных условиях '
        'эксплуатации (повышенная сейсмичность, вечная мерзлота). \n\n'
        f"Сайт: <a href=\"{link}\">Открыть сайт</a>\n\n"
        'Генеральный директор: Кувшинова Елена Валерьевна'
    )
    type_value = 'Логотип'
    organization_id = 3
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info_builder,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")
@router.callback_query(F.data == 'defender')
async def defender_info(callback:CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRvL7c\">ул. Ядринцевская, 72</a>'
    text = (
        f'{card} \n\n' 
        'Описание: Услуги по обеспечению безопасности людей, имущества и объектов. Работа с частными и корпоративными '
        'клиентами: охрана, сопровождение, пропускной режим, консультации и безопасность на мероприятиях. \n\n'
        'Генеральный директор: Петрина Василий Михайлович'
    )
    type_value = 'Логотип'
    organization_id = 4
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info_builder,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")

@router.callback_query(F.data == 'builder_navigation')
async def builder_navigation(callback: CallbackQuery):
    link = '<a href=\"https://yandex.ru/maps/-/CLBRvL7c\">ул. Ядринцевская, 72</a>'
    await callback.message.answer(f"""
г. Новосибирск, {link} 1 этаж.
Вход: со стороны ул.Ядринцевская, под кафе 'GeLatte'. 
Офис работает до 18:00. Попасть к нам можно только по предварительной договорённости.
                                """,
                                reply_markup=kb_info.inline_back_info_bonus,
                                parse_mode="HTML",
                                disable_web_page_preview=True 
                                  )


@router.callback_query(F.data == 'shop')
async def shop_info(callback:CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLBRzA3u\">Красный просп., 49</a>'
    link = 'https://www.skolko-mozhno.ru/'
    link_vk = 'https://vk.com/skolkomozhno.brand'
    link_telegram = 'https://t.me/skolkomozhnobrand'
    link_insta = 'https://www.instagram.com/skolkomozhno.brand'
    text = (
        f'{card} \n\n'
        '«Сколько? Можно» — это бренд мужской и женской одежды, в котором привычное переплетается с дерзким. Мы создаём '
        'нестандартные вещи, которые помогают выйти за рамки привычного гардероба. Мы уверены, что каждый человек имеет '
        'право на самовыражение, и наша одежда — это не просто вещи, а способ показать миру свою истинную сущность. \n\n'
        'Бренд представлен на онлайн и офлайн-площадках. Concept store нашего бренда расположен на Красном проспекте, 49 — '
        'это пространство, где можно познакомиться с философией «Сколько? Можно» вживую, увидеть коллекции и вдохновиться атмосферой. \n\n'
        'Наши соцсети:\n'
        f"<a href=\"{link_vk}\">Наш Вконтакте</a>\n"
        f"<a href=\"{link_telegram}\">Наш Telegram</a>\n"
        f"<a href=\"{link_insta}\">Наш Instagram</a>\n\n"
        f"Наш сайт: <a href=\"{link}\">Открыть сайт</a>\n\n"
        'Руководитель направления: Маркова Мария Сергеевна'
    )
    type_value = 'Логотип'
    organization_id = 5
    file_records = await rq_link.get_commission_photo(type_value, organization_id, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path)),
                    caption=text,  
                    reply_markup=kb_info.inline_back_info_shop,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")
@router.callback_query(F.data == 'farm')
async def farm_info(callback:CallbackQuery):
    text = (
        'Внутри группы компании мы развиваем производство качественных и натуральных продуктов сельского хозяйства. Мы '
        'выращиваем экологически чистые культуры, разводим скот и заботимся о наших курах! Наша цель – обеспечивать  '
        'потребителей свежими и полезными продуктами, выращенными с любовью к земле и животным. \n\n'
        'Руководитель направления: Титаев Павел Сергеевич'
)
    await callback.message.answer(text, reply_markup=kb_info.inline_back_info)

@router.callback_query(F.data == 'bonus')
async def bonus_info(callback: CallbackQuery):
    await callback.message.answer('Наши бонусы:',reply_markup=kb_info.inline_info_bonus)
@router.callback_query(F.data == 'dms')
async def dms_info(callback: CallbackQuery, state: FSMContext):
    text = (
        'Сейчас я расскажу тебе о Добровольном Медицинском Страховании (ДМС) в нашей компании. Это важная часть твоего социального пакета!\n\n'
        '• Условия получения: ДМС предоставляется сотрудникам после года работы в компании (обязательно напомни о себе, когда подойдет время).\n'
        '• В отдельных случаях, мы можем рассмотреть возможность предоставления ДМС раньше. Обратись в отдел HR или к своему руководителю для индивидуального рассмотрения твоего вопроса!\n'
        '• Ты можешь использовать ДМС по своему усмотрению, направление от врача не требуется.\n'
        '• Твой лимит по ДМС составляет 30 000 рублей в год.\n\n'
        'Как воспользоваться ДМС: (Пошаговая инструкция) \n'
        '1. Выбор клиники и услуги:\n'
        ' •  Ознакомься со списком клиник, доступных по ДМС, в специальной памятке.\n'
        ' •  Выбери клинику и необходимую услугу.\n'
        ' •  Запишись на прием и узнай стоимость услуги.\n'
        'Важно: Список клиник в памятке не полный. Если нужной клиники нет в списке, уточни возможность обслуживания в ней у менеджера. Возможно, у нас уже заключен договор с этой клиникой!\n'
        '2. Связь с менеджером страховой:\n'
        ' •  Найди контактный номер телефона своего менеджера в страховой компании в памятке.\n'
        ' •  Свяжись с менеджером удобным способом (звонок или WhatsApp).\n'
        ' •  Предоставь следующую информацию:\n'
        '   *  Твое имя и фамилию\n'
        '   *  Название нашей компании.\n '
        '   *  Название клиники и её адрес.\n '
        '   *  Название услуги или список необходимых анализов (если это сдача анализов).\n '
        '   *  Стоимость услуги (или максимальную возможную стоимость, если точную узнать не удалось).\n'
        '3. Получение гарантийного письма:\n'
        '  •  Страховая компания направит гарантийное письмо на электронную почту выбранной тобой клиники.\n'
        '4. Посещение клиники:\n'
        '  •  Приходи в клинику в назначенную дату и время.\n '
        '  •  На стойке администратора сообщи, что ты обслуживаешься по программе ДМС.\n\n'
        'Готово! Если у тебя остались вопросы по ДМС, ты всегда можешь обратиться в отдел HR или повторно обратиться ко мне! 👍\n\n'
    )
    await callback.message.answer(text, reply_markup=kb_info.inline_back_info_bonus, parse_mode="HTML")
    try:
        file_type = 'Информация о ДМС'
        await state.update_data(sample_type=file_type)
        telegram_id = callback.from_user.id
        user_number = await rq_reg.get_user_number(telegram_id)
        user_id = await rq_reg.get_user_id(user_number)
        await callback.answer("⏳ Ищем файлы...")
        files = await rq_link.get_link_dms(user_id, file_type)
        if files:
            file_groups = [files[i:i+2] for i in range(0, len(files), 2)]
            sent_groups = 0
            for group in file_groups:
                media_group = []
                for file in group:
                    file_path = rq_link.BASE_DIR / file.file_path
                    print(f"Проверяем файл: {file_path}")
                    print(f"Файл существует: {file_path.exists()}")
                    if not file_path.exists():
                        await callback.message.answer(f"Файл не найден: {file.file_path}")
                        continue
                    try:
                        with open(file_path, 'rb') as test_file:
                            test_file.read(1024)
                        media = InputMediaDocument(
                            media=FSInputFile(file_path),
                            caption=f"{file.type}" if len(group) == 1 else None
                        )
                        media_group.append(media)
                    except Exception as file_error:
                        await callback.message.answer(f"Файл недоступен: {file.file_path} - {str(file_error)}")
                        continue
                if media_group:
                    try:
                        if len(media_group) == 1:
                            await callback.message.answer_document(
                                document=media_group[0].media,
                                caption=media_group[0].caption
                            )
                        else:
                            await callback.message.answer_media_group(media=media_group)
                        sent_groups += 1
                        if sent_groups < len(file_groups):
                            await asyncio.sleep(2)
                    except Exception as e:
                        await callback.message.answer(f"Ошибка при отправке группы файлов: {str(e)}")
                        print(f"Детали ошибки: {type(e).__name__}: {e}")
            total_files = len(files)
        else:
            await callback.message.answer("Файлы по ДМС не найдены.")
            
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {str(e)}")
        print(f"Ошибка в dms_info: {e}")
 

@router.callback_query(F.data == 'fitness')
async def fitness_info(callback: CallbackQuery):
    card = '<a href=\"https://yandex.ru/maps/-/CLcne4l1\"> ул. Трудовая, 25, </a>' 
    text = (
    'Хочу рассказать тебе о нашей программе корпоративного фитнеса!\n'
    'Каждую среду у нас есть отличная возможность размяться и зарядиться энергией на весь день! 🤸‍♀️\n'
    'Что: Корпоративный фитнес. Никаких сложных упражнений, только разминка и поддержание здоровья!\n'
    'Когда: Каждую среду с 11:00 до 12:00.\n'
    f'Где: {card} 1 этаж (вход за колонной). 📍\n'
    'Что будем делать? У нас разные направления:\n'
    '•  🧘‍♀️ Здоровая спина\n'
    '•  🤸‍♀️ Растяжка\n'
    '•  💪 Силовая тренировка\n'
    '•  🧽 МФР тренировка (миофасциальный релиз)\n'
    'Все тренировки адаптированы для разных уровней подготовки, так что не переживай, если ты новичок!\n'
    'Что взять с собой? Самое главное - спортивную или просто удобную, не сковывающую движения одежду. Спортивная обувь не нужна! 👚 В студии есть раздевалка, где можно переодеться.\n'
    'Присоединяйся! Это отличный способ познакомиться с коллегами, взбодриться и поддержать свое здоровье! 😉\n'
    'Если тебе не подходит такой формат тренировок, то в компании предусмотрена программа компенсаций занятий спортом, более подробно смотри в разделе компенсации.\n\n'
    'Есть вопросы? Спрашивай! 💬'
    )
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info_bonus, parse_mode='HTML')
async def dms_info(callback: CallbackQuery):
    text = (
        'Сейчас я расскажу тебе о Добровольном Медицинском Страховании (ДМС) в нашей компании. Это важная часть твоего социального пакета!\n\n'
        '• Условия получения: ДМС предоставляется сотрудникам после года работы в компании (обязательно напомни о себе, когда подойдет время).\n'
        '• В отдельных случаях, мы можем рассмотреть возможность предоставления ДМС раньше. Обратись в отдел HR или к своему руководителю для индивидуального рассмотрения твоего вопроса!\n'
        '• Ты можешь использовать ДМС по своему усмотрению, направление от врача не требуется.\n'
        '• Твой лимит по ДМС составляет 30 000 рублей в год.\n\n'
        'Как воспользоваться ДМС: (Пошаговая инструкция) \n'
        '1. Выбор клиники и услуги:\n'
        ' •  Ознакомься со списком клиник, доступных по ДМС, в специальной памятке.\n'
        ' •  Выбери клинику и необходимую услугу.\n'
        ' •  Запишись на прием и узнай стоимость услуги.\n'
        'Важно: Список клиник в памятке не полный. Если нужной клиники нет в списке, уточни возможность обслуживания в ней у менеджера. Возможно, у нас уже заключен договор с этой клиникой!\n'
        '2. Связь с менеджером страховой:\n'
        ' •  Найди контактный номер телефона своего менеджера в страховой компании в памятке.\n'
        ' •  Свяжись с менеджером удобным способом (звонок или WhatsApp).\n'
        ' •  Предоставь следующую информацию:\n'
        '    *  Твое имя и фамилию\n'
        '    *  Название нашей компании.\n '
        '   *  Название клиники и её адрес.\n '
        '   *  Название услуги или список необходимых анализов (если это сдача анализов).\n '
        '   *  Стоимость услуги (или максимальную возможную стоимость, если точную узнать не удалось).\n'
        '3. Получение гарантийного письма:\n'
        '  •  Страховая компания направит гарантийное письмо на электронную почту выбранной тобой клиники.\n'
        '4. Посещение клиники:\n'
        '  •  Приходи в клинику в назначенную дату и время.\n '
        ' •  На стойке администратора сообщи, что ты обслуживаешься по программе ДМС.\n\n'
        'Готово! Если у тебя остались вопросы по ДМС, ты всегда можешь обратиться в отдел HR или повторно обратиться ко мне! 👍'
    )
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info_bonus)
@router.callback_query(F.data == 'compensation')
async def compensation_info(callback: CallbackQuery):
    text = (
    'Хочу рассказать тебе о наших компенсациях! Компания поддерживает твои увлечения и развитие!\n\n'
    'Мы готовы компенсировать часть твоих расходов на:\n'
    '•  🤸‍♀️ Спорт: Фитнес, танцы, йога и другие виды активного образа жизни.\n'
    '•  📚 Обучение: Курсы, тренинги и семинары, как связанные с работой, так и для личностного развития.\n'
    '•  🎨 Хобби: Креативные курсы, рукоделие, музыка, кулинария и другие увлечения.\n'
    'Сколько компенсируем?\n'
    '•  50% от стоимости занятий или курсов, но не более 25 000 руб..\n'
    '•  Максимальная сумма компенсации в год: 25 000 руб.\n\n'
    'Как получить компенсацию? Порядок действий:\n'
    '1. Будь с нами не менее 3 месяцев: Ты должен быть официально трудоустроен в компании минимум 3 месяца.\n'
    '2. Собирай документы: Сохраняй все чеки, квитанции и договоры, подтверждающие твои расходы.\n'
    '3. Предоставь документы бухгалтеру: Передай копии подтверждающих документов главному бухгалтеру.\n'
    '4. Подай заявление: Сделай это не позднее 30 дней после окончания оплаченного периода или приобретения товара/услуги.\n'
    'Важно: Компенсируются только затраты, подтвержденные документально (чеки, квитанции, договоры и т.п.).\n\n'
    'Альтернативный вариант:\n'
    'Если тебе нужна большая сумма, ты можешь получить полную сумму на приобретение товара/услуги в виде займа, '
    'а потом постепенно возвращать ее из зарплаты. Для этого нужно будет заключить договор займа.\n\n'
    'Мы рады поддержать тебя в твоих увлечениях и стремлении к развитию! 😉 Есть вопросы? Спрашивай! 💬'
    )
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info_bonus)
@router.callback_query(F.data == 'referral')
async def referral_info(callback: CallbackQuery):
    text = (
    'Хочу рассказать тебе про нашу реферальную программу!\n'
    'У нас действует программа "Приведи друга - получи бонус"! 🤝 Если ты знаешь талантливого человека, который отлично\n'
    'впишется в нашу команду, расскажи ему о нас!\n\n'
    'Как это работает?\n'
    '1. Узнай об актуальных вакансиях. Это можно сделать в HR-отделе или по ссылке: https://novosibirsk.hh.ru/employer/1919223 \n'
    '2. Порекомендуй своим друзьям и знакомым.\n'
    '3. Если твой друг успешно пройдет собеседование и станет частью нашей команды, ты получишь бонус после\n'
    'прохождения им испытательного срока! 🎉\n\n'
    'Это отличная возможность помочь своим друзьям найти работу и получить приятный бонус за рекомендацию! 😉\n'
    'Если у тебя остались вопросы, ты всегда можешь обратиться в отдел HR или повторно обратиться ко мне! \n'
    )
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info_bonus)
@router.callback_query(F.data == 'food')
async def food_info(callback: CallbackQuery):
    link = 'https://docs.google.com/spreadsheets/d/1hrK3uKH6yE0Cb_-zlPSkg2VvCpYn3f-LDEq-GoN7mb4/edit#gid=0'
    text = (
    'Хочешь вкусно обедать на работе? Тогда читай про наше корпоративное питание! 🍱\n\n'

    '1. Выбор меню: Каждую неделю (в четверг-пятницу) в корпоративном чате публикуется меню обедов на следующую рабочую неделю. Меню единое для всех.\n'
    f"2. Подача заявки: Ты сам заказываешь обеды через <a href=\"{link}\">Google-таблицут</a>  "
    'Просто поставь "1" напротив своей фамилии в дни недели, когда хочешь заказать обед.\n'
    '3. Срок подачи заявки: Крайний срок – пятница, 17:00. Следи за объявлениями в корпоративном чате, дедлайн может меняться!\n'
    '4. Проверка заявки: В понедельник проверяй свою заявку в Google-таблице, чтобы убедиться, что все верно.\n'
    '5. Отмена или дозаказ:\n'
    '   •  Отменить заказ можно до 8:00 дня доставки обеда, просто изменив заявку в таблице и уведомив об этом менеджера.\n'
    '   •  Дозаказать обед можно до 17:00 предыдущего дня, изменив заявку в таблице и уведомив ответственного менеджера.\n'
    '6. Оплата и компенсация:\n'
    '   •  Компания компенсирует часть стоимости обедов.\n'
    '   •  Стоимость обеда для тебя - 282 рубля.\n'
    '   •  Твоя часть будет удержана из заработной платы.\n'
    '7. Доставка и выдача:\n'
    '   •  Обеды доставляют примерно в 10:00.\n'
    '   •  Ищи их на кухне на 8 этаже.\n'
    '8. Изменения: Обо всех изменениях в порядке питания (меню, время доставки и т.д.) мы будем оперативно сообщать в корпоративном чате.\n\n'
    'Обо всех изменениях сразу пишем в чат! 💬\n\n'
    'Вкусно, удобно и выгодно! 😉 Остались вопросы? Не стесняйся задавать!'
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb_info.inline_back_info_bonus,disable_web_page_preview=True)

@router.callback_query(F.data == 'employment')
async def employment_info(callback: CallbackQuery):
    await callback.message.answer('Какое направление тебя интересует?', reply_markup=kb_info.inline_employment_info)
@router.callback_query(F.data == 'manufacture')
async def manufacture_info (callback: CallbackQuery):
    text = (
    'Привет! 👋 Добро пожаловать на завод! Вот шаги для трудоустройства:\n\n'
    '1. Проверка службой безопасности: Это стандартная процедура, необходимая для обеспечения безопасности на предприятии.\n'
    'Необходимо будет заполнить анкету и ответить на несколько вопросов.\n' 
    '2. Медкомиссия:\n'
    '  •  После прохождения проверки службой безопасности специалист по охране труда выдаст направление на медкомиссию.\n'
    '  •  Вся подробная информация, есть в памятке. Обязательно ознакомься с ней.\n'
    '  •  Прохождение медкомисии происходит за счёт средств организации, Вам ничего оплачивать не нужно будет.\n' 
    '  •  Напоминаю, что сдача анализов происходит на голодный желудок, до 10 часов утра.\n'
    '3. Трудоустройство:\n'
    '  •  Приходи в отдел кадров по адресу: Ядринцевская, 72, 8 этаж. На этаж организованна пропускная система.'
    ' Доступ на этаж с менеджером. Все необходимые контакты продублированы ниже.\n'
    '  •  Время работы отдела кадров: с 10:00 до 16:00 в любой рабочий день.\n'
    '  •  Рекомендуем заранее связаться с менеджером и сообщить о своем визите.\n'
    '  •  Список документов для трудоустройства:\n'
    '✅ Паспорт и прописка\n'
    '✅ СНИЛС\n'
    '✅ ИНН (достаточно просто номера)\n'
    '✅ Трудовая книжка (бумажная или выписка из электронной)\n'
    '✅ Документ об образовании, удостоверения (если есть)\n'
    '✅ Свидетельства о рождении детей до 14 лет (если есть)\n'
    '4. Обучение по охране труда:\n'
    '  •  Обязательный этап для всех новых сотрудников. Свяжись со специалистом по охране труда, чтобы получить инструкции и пройти обучение.\n'
    'Обучение проходит в онлайн формате.\n'
    '  •  Обучение может занять до 5 рабочих дней, в зависимости от программы.' 
    'Актуальную дату выхода ты можешь узнать у мастера своего участка или директора по производству.\n\n'
    'Необходимые контакты:\n'
    '•  Специалист по охране труда: +7 (913) 758-04-80 - по вопросам медкомиссии и обучения по охране труда.\n'
    '•  Отдел кадров: +7 (962) 837-87-62 - по вопросам оформления трудовых отношений.\n'
    '•  Начальник производства: +7 (953) 872-74-16 - для оперативных вопросов по работе.\n\n'
    'Удачи в процессе трудоустройства! Если у тебя возникнут вопросы, не стесняйся обращаться!')
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info)
    type_value = 'Медецинская комиссия'
    await callback.answer("⏳ Ищем файлы...")

    file_records = await rq_link.get_commission_photo(type_value, organization_id = None, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path))
            )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")

@router.callback_query(F.data == 'office_job')
async def office_job_info (callback: CallbackQuery):
    text = (
        'Привет! 👋 Добро пожаловать в нашу команду! Этот бот поможет тебе разобраться с порядком трудоустройства.\n\n'
        'Твой офис находится на Ядринцевской, 72?\n'
        '•  Тогда в первый рабочий день приходи в офис, на 8 этаж к 09:30 с документами. Тебя встретит HR-менеджер и сопроводит на оформление.\n'
        'Список необходимых документов для трудоустройства:\n'
        '✅ Паспорт (и прописка)\n'
        '✅ СНИЛС\n'
        '✅ ИНН (достаточно знать номер)\n'
        '✅ Трудовая книжка (бумажная или выписка из электронной)\n'
        '✅ Документ об образовании (если есть)\n'
        '✅ Свидетельства о рождении детей до 14 лет (если есть)\n\n'
        'Как проходит оформление:\n'
        'Шаг 1 – Подготовка и подписание документов тобой:\n'
        '•  Поздравляем, ты официально в нашей команде с первого дня!\n'
        'Мы оформляем и подписываем пакет документов, а также знакомим со всеми внутренними положениями компании.'
        ' Это может занять некоторое время.\n'
        'У тебя будет время внимательно изучить всю информацию.\n'
        'Шаг 2 – Подписание документов работодателем:\n'
        'После подписания тобой, документы передаются на подпись генеральному директору.\n'
        'Это занимает обычно 2-3 дня.\n'
        'После подписания один экземпляр договора вернется тебе, а второй останется у нас.\n\n'
        'Удачи с началом работы! Если у тебя возникнут вопросы на любом этапе, не стесняйся задавать!')
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info)
@router.callback_query(F.data == 'vahta')
async def vahta_info(callback:CallbackQuery):
    text = (
    'Привет! 👋 Рады приветствовать тебя в нашей команде строителей! Этот бот поможет тебе сориентироваться в процессе трудоустройства.\n\n'
    'Вот шаги, которые тебе предстоит пройти:\n'
    '1. Проверка службой безопасности:\n'
    '  •  Необходимо заполнить анкету\n'
    '  •  Начальник службы безопасности свяжется с тобой по телефону, чтобы задать несколько вопросов.\n'
    '2. Предоставление документов:\n'
    '  •  Необходимо направить сканы или фотографии следующих документов:\n'
    '    ✅ Паспорт (и прописка)\n'
    '    ✅ СНИЛС\n'
    '    ✅ ИНН (достаточно просто номера)\n'
    '    ✅ Трудовая книжка (бумажная или выписка из электронной)\n'
    '    ✅ Документ об образовании и удостоверения (если есть)\n'
    '    ✅ Свидетельства о рождении детей до 14 лет (если есть)\n'
    '  •  Это необходимо, чтобы мы могли подготовиться к твоему выходу.\n'
    '3. Медкомиссия:\n'
    '  •  Специалист по охране труда свяжется с тобой для уточнения информации и выдаст направление на медкомиссию.\n'
    '  •  Медкомиссию ты можешь пройти:\n'
    '    *  По месту нахождения объекта вахты.\n'
    '    *  Или, если есть время, по месту постоянного проживания.\n'
    '  •  Оплату медкомиссии берет на себя работодатель.\n'
    '4. Трудоустройство:\n'
    '  •  Если ты находишься в Новосибирске, мы будем рады видеть тебя в офисе по адресу: Ядринцевская, 72, 8 этаж. Дату и время согласуем индивидуально.\n'
    '  •  Если ты находишься в другом городе, мы направим все необходимые документы для подписания по электронной почте.\n'
    '5. Обучение по охране труда и промышленной безопасности:\n'
    '  •  В зависимости от твоей должности, может потребоваться дополнительное обучение. Мы предоставим всю необходимую информацию.\n'
    '6. Покупка билетов:\n'
    '  •  Мы согласуем с тобой удобную дату и маршрут, а затем приобретем билеты до места работы.\n\n'
    'Удачи в процессе трудоустройства! Если возникнут вопросы, не стесняйся спрашивать!')
    await callback.message.answer(text,reply_markup=kb_info.inline_back_info)
"""    type_value = 'Медецинская комиссия'
    await callback.answer("⏳ Ищем файлы...")

    file_records = await rq_link.get_commission_photo(type_value, organization_id = None, department_id = None)
    if file_records:
        for file_record in file_records:
            file_path = rq_link.BASE_DIR / file_record.file_path
            if file_path.exists() and file_path.is_file():
                await callback.message.answer_photo(
                    photo=FSInputFile(path=str(file_path))
            )
            else:
                await callback.message.answer("Файл не найден на сервере")
    else:
        await callback.message.answer("Файл не найден в базе данных")"""

@router.callback_query(F.data == 'motivation')
async def motivation(callback: CallbackQuery):
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    if button_text == 'Структура':
        type = 'Структура ПТО'
    else:
        type=button_text
    telegram_id =  callback.from_user.id
    user_number = await rq_reg.get_user_number(telegram_id)
    user_id = await rq_reg.get_user_id(user_number) 
    file_link = await rq_reg.get_private_files(user_id=user_id, type_=type)
    if not file_link:
        await callback.message.answer("Файл не найден")
        return
    await callback.message.answer(f'<a href=\"{file_link}\">Открыть файл</a>',
                                      parse_mode='HTML', reply_markup=kb_info.inline_back_info)