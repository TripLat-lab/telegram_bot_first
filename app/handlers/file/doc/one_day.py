from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
import logging
from aiogram.types import BufferedInputFile
from pathlib import Path
from typing import Optional
import asyncio

import app.keyboard.one_day_kb as kb_start
import app.keyboard.total_ifo_kb as kb_info
import app.request.link_files.sample_link_file_rq as rq_link
import app.request.registered_rq as rq_reg




router = Router()
logger = logging.getLogger(__name__)



async def send_pdf_file(
    callback,
    file_path: Path,
    caption: Optional[str] = None,
    reply_markup = None,
    parse_mode = None
):
    """
    Отправка PDF через BufferedInputFile с возможностью указать caption и reply_markup.
    """

    if not file_path.exists() or not file_path.is_file():
        await callback.message.answer("Файл не найден")
        return

    data = file_path.read_bytes()
    input_file = BufferedInputFile(data, filename=file_path.name)

    await callback.message.answer_document(
        document=input_file,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode = parse_mode
    )


@router.message(F.text == "Первый рабочий день")
async def one_day_select_user_id(message: Message):
   telegram_id = message.from_user.id
   user_number = await rq_reg.get_user_number(telegram_id)
   return_user_data = await rq_reg.select_users_department_and_mentor(user_number)
   if return_user_data is not None:
        name, username, number, id = return_user_data
   else:
        username = number = id = " "
        name = 'Иванов Алексей Андреевич'
   department = await rq_reg.get_user_name_or_dept(id)
   if not department:
         text_v1 = f'•  Непосредственный руководитель: {name}, отдела: {department} контактный телефон: {number}, ссылка на его телеграмм аккаунт: {username}'
         return text_v1
   text_v1 = f'•  Непосредственный руководитель: {name}, ссылка на его телеграмм аккаунт: {username}'
   cafe_1 = '<a href="https://yandex.ru/maps/-/CLWgr43x"> “GeLatte”, </a>'
   cafe_2 = '<a href="https://yandex.ru/maps/-/CLWgrRLD"> “BarBQ” </a>'
   cafe_3 = '<a href="https://yandex.ru/maps/-/CLWgrRLD"> “Spar” </a>'
   cafe_4 = '<a href="https://yandex.ru/maps/-/CLWgrRLD"> “Калина-малина” </a>'
   cafe_5 = '<a href="https://yandex.ru/maps/-/CLWgv4YZ"> "Ярче!" </a>'
   cafe_6 = '<a href="https://yandex.ru/maps/-/CLWgv6ze"> “Мини-маркет” </a>'

   number_card = '<a href="https://docs.google.com/spreadsheets/d/1xwpOeGHJyx6kHafZM7NW8Da8rJJXGL1H/edit?usp=sharing&ouid=107658314868002617699&rtpof=true&sd=true">карточке</a>'
   card = '<a href="https://yandex.ru/maps/-/CLBRvKIF">ул. Ядринцевская, 72,</a>'
   text = f"""Добро пожаловать в команду! Чтобы Твой первый день был максимально комфортным и понятным, пожалуйста, ознакомься с информацией ниже.
\n<b>1. Информация об офисе</b>
   •  Адрес офиса: {card} 8 этаж
\n•  Ближайшие парковки:
   •  Общественная парковка вдоль улицы Ядринцевская (бесплатная, но может быть сложно найти место после 10 часов)
\n•  Ближайшие кафе и рестораны:
   • Кафе {cafe_1} (Ядринцевская, 72, 2 этаж)
   • Гриль-бар {cafe_2} (Каменская, 44, 5 минут) 
   • Магазины с готовой едой {cafe_3} и {cafe_4} (Каменская, 44, 5 минут)
   • Продуктовые магазины: Супермаркет {cafe_5} (Ядринцевская, 68/1), {cafe_6} (Трудовая 25/1)
   • Также в компании организовано корпоративное питание, стоимость комплексного обеда 282 руб.
\n•  Дресс-код:
   •  В нашей компании нет строгого дресс-кода, при выборе аутфита руководствуемся принципами уместности и аккуратности.
\n<b>2. Ваш первый рабочий день</b>
   •  Время прибытия в офис: прибыть в офис к 09:30.
   •  Вас встретит твой нанимающий HR. Вы можете связаться с нами по номеру телефону: +7 (962) 837-87-62 
   •  Документы для трудоустройства:
 \n ✅ Паспорт и прописка
 ✅ СНИЛС
 ✅ ИНН (достаточно просто номера)
 ✅ Трудовая книжка (бумажная или выписка из электронной) 
 ✅ Документ об образовании (если есть)
 ✅ Свидетельства о рождении детей до 14 лет (если есть)
\n<b>3. Доступы к корпоративным сервисам</b>
   •  Пропуск в офис: пропуск будет выдан на ресепшене помощником руководителя, не забудьте подойти к ней в первый рабочий день.
   •  Доступы:  доступ к учётной системе ты получишь в личные сообщения
  •  Доступ к корпоративным сервисам (Битрикс24) будет предоставлен в течение первого рабочего дня.
Ваша команда
  {text_v1}
  • Контакты остальной команды ты можешь найти в {number_card} сотрудников 
\nЕсли у вас возникнут какие-либо вопросы до вашего первого рабочего дня, не стесняйтесь связаться с нами. Мы с нетерпением ждем встречи!
            """
   await message.answer(f"{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_start.inline_next_key_one)
@router.callback_query(F.data == 'next_one')
async def get_company_info_GK(callback: CallbackQuery):
    type_value = 'Информация о ГК'
    file_link = await rq_link.get_public_files_link(name=type_value)
    link = f'<a href="{file_link}"> Наши основные направления </a>'
    text = ('Отлично! Теперь, когда мы немного познакомились, предлагаю тебе окунуться в мир нашей группы компаний'
    f' "ПМК". \n\n🧭 Чтобы тебе было легче ориентироваться, изучи, пожалуйста, все <b>{link}</b>')
    if file_link is None:
        await callback.message.answer(f'Файл не найден\n\n{text}', reply_markup=kb_start.inline_next_key_two, parse_mode='HTML')
    await callback.message.answer(f'{text}',reply_markup=kb_start.inline_next_key_two, parse_mode='HTML')

@router.callback_query(F.data == 'next_two|next_three')
async def get_company_info(callback: CallbackQuery):
      try:
        type_value = 'Информация о компании'
        file_link = await rq_link.get_public_files_link(name=type_value)
        link = f'<a href="{file_link}">историю компании, ценности и миссию</a>'
        text =( f'🌪 Теперь углубимся в {link}.\n'
            f'\nМы рады представить вам не просто набор фактов, а живую' 
            f'\nисторию, философию и душу нашей компании. Углубимся в то,'
            f'\nкто мы есть, откуда пришли и куда движемся, а главное –'
            f'\nпочему каждый из нас является неотъемлемой частью этого пути.'
            
         )
        if file_link is None:
            await callback.message.answer(f'Файл не найден\n\n{text}', reply_markup=kb_start.inline_next_key_three, parse_mode='HTML')
        await callback.message.answer(f'{text}',reply_markup=kb_start.inline_next_key_three, parse_mode='HTML')
      except Exception as e:
         await callback.message.answer(f"Ошибка: {e}")

# Клавиатура для "Следующее видео"
def next_video_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Следующее видео", callback_data="next_video")]]
    )

# Универсальная функция для старта последовательности видео
async def start_video_sequence(callback: CallbackQuery, state: FSMContext, video_links: list[str], video_names: list[str],
                                intro_text: str, final_kb: InlineKeyboardMarkup = None, parse_mode=None):
    if not video_links:
        await callback.message.answer("Видео не найдено")
        return

    # Сохраняем данные в state
    await state.update_data(
        video_links=video_links,
        video_names=video_names,
        current_index=0,
        final_kb=final_kb,
        parse_mode=parse_mode
    )

    # Отправляем интро сообщение
    await callback.message.answer(intro_text, parse_mode=parse_mode)
    await asyncio.sleep(1.5)

    # Отправляем первое видео
    text = f"{video_names[0]}\n{video_links[0]}" if video_names[0] else video_links[0]
    # Если видео больше одного, показываем кнопку "Следующее видео"
    if len(video_links) > 1:
        await callback.message.answer(text, reply_markup=next_video_kb(), parse_mode=parse_mode)
    else:
        # Если видео одно, сразу используем финальную клавиатуру
        if final_kb:
            await callback.message.answer(text, reply_markup=final_kb, parse_mode=parse_mode)
        else:
            await callback.message.answer(text, parse_mode=parse_mode)

# Универсальный хэндлер для кнопки "Следующее видео"
@router.callback_query(F.data == "next_video")
async def next_video(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    links = data.get("video_links", [])
    names = data.get("video_names", [])
    index = data.get("current_index", 0)
    parse_mode='HTML'
    final_kb = data.get("final_kb")  # Финальная клавиатура после последнего видео

    if index + 1 < len(links):
        index += 1
        await state.update_data(current_index=index)
        text = f"{names[index]}\n{links[index]}" if names[index] else links[index]

        # Если это последнее видео, показываем финальную клавиатуру
        if index + 1 == len(links) and final_kb:
            await callback.message.answer(text, reply_markup=final_kb, parse_mode=parse_mode)
        else:
            await callback.message.answer(text, reply_markup=next_video_kb(), parse_mode=parse_mode)




@router.callback_query(F.data == 'next_three')
async def get_video_publick(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    user_number = await rq_reg.get_user_number(telegram_id)
    user = await rq_link.get_user_name(user_number)
    department_name = await rq_link.get_file_id_for_dept_name(user)
    dept_link, public_link = await rq_link.get_file_id_for_link_type(department_name)

    video_links = []
    video_names = []

    if public_link:
        video_links.append(public_link)
        video_names.append("")  # можно добавить название, если есть

    if dept_link:
        video_links.append(dept_link)
        video_names.append("")

    intro_text = (
        "Хэй, у нас гости. Кажется теперь <b>собственник группы компаний Алексей Андреевич Иванов</b>, "
        "и <b>твой непосредственный руководитель</b> хотят лично поприветствовать тебя и сказать несколько слов."
        "Они хотят лично поприветствовать тебя и поделиться своим напутствием. Послушай их внимательно! "
    )

    # Финальная клавиатура после последнего видео
    final_kb = kb_start.inline_next_key_four

    await start_video_sequence(callback, state, video_links, video_names, intro_text, final_kb, parse_mode='HTML')

@router.callback_query(F.data == 'next_four')
async def org_stuctura(callback: CallbackQuery):
   text = ('Чтобы тебе было легче ориентироваться и понимать, как тут всё устроено, мы подготовили для тебя кое-что важное. ' 
           '🏫 Этот шаг полностью посвящён нашей <b>организационной структуре.</b>')
   type = 'Орг. структура'
   file_records = await rq_link.get_commission_photo(type, organization_id = None, department_id = None)
   if file_records:
       for file_record in file_records:
         file_path = rq_link.BASE_DIR / file_record.file_path
         if file_path.exists() and file_path.is_file():
           await callback.message.answer_photo(
               photo=FSInputFile(path=str(file_path)),
               caption=text,  
               reply_markup=kb_start.inline_next_key_five,
               parse_mode="HTML",
               disable_web_page_preview=True,
                    )
         else:
            await callback.message.answer("Файл не найден на сервере")

# Пример хэндлера для next_five
@router.callback_query(F.data == 'next_five')
async def top_menedment(callback: CallbackQuery, state: FSMContext):
    type = "Топ менеджер"
    intro_text = (
        "🚀 Давай познакомимся с остальными <b>топ-менеджерами компании.</b> "
        "Эти видео — личное обращение от нашего высшего руководства, "
        "которое желает вам успешного старта, быстрого погружения в наши процессы "
        "и плодотворной работы. С нами вы найдете возможности для роста и развития."
    )

    links, names = await rq_link.get_Dept_name_video(type)
    final_kb = kb_start.inline_next_key_six
    await start_video_sequence(callback, state, links, names, intro_text, final_kb, parse_mode='HTML')

# Пример хэндлера для next_six
@router.callback_query(F.data == 'next_six')
async def out_department(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    user_number = await rq_reg.get_user_number(telegram_id)
    user_id = await rq_reg.get_user_id(user_number)
    department_name = await rq_link.get_file_id_for_dept_name(user_id)

    intro_text = (
        "👫 В каждом нашем отделе, как и полагается, есть свой руководитель и команда линейных сотрудников. "
        "С главой своего отдела ты уже, я вижу, познакомился. Теперь, чтобы ты точно знал, кто есть кто и к кому "
        "обращаться по другим вопросам, давай <b>познакомимся с руководителями остальных отделов.</b>"
    )

    links, names = await rq_link.get_Dept_name_video(
            exclude_type=department_name,
            user_dept=department_name
    )
    final_kb = kb_start.inline_next_key_seven
    await start_video_sequence(callback, state, links, names, intro_text, final_kb, parse_mode='HTML')

@router.callback_query(F.data == 'next_seven')
async def regulations(callback: CallbackQuery):
    name = 'Регламент'
    regulations_all = await rq_link.get_regulations_all(name)
    await callback.message.answer(f'А теперь давай углубимся в детали. Чтобы ты мог глубже понять функционал каждого отдела, ' 
                                  'давай-ка изучим <b>регламенты работы каждого отдела</b> 📚. '
                                  'Это поможет тебе разобраться в функционале отделов досконально и подробно объяснит, как всё работает "изнутри".',
                                   reply_markup=kb_start.regulations_all(regulations_all), parse_mode='HTML')
    
@router.callback_query(F.data.startswith('regulation|'))
async def uploud_regulation_link(callback: CallbackQuery):
    parts = callback.data.split('|')
    file_id = int(parts[1])
    link = await rq_link.upload_link(file_id)
    await callback.message.answer(f'<a href="{link}">Открыть файл</a>', parse_mode="HTML", reply_markup=kb_start.inline_next_key_eight)

@router.callback_query(F.data == 'next_eight')
async def process_Instructions(callback: CallbackQuery, state: FSMContext):
   try:
      telegram_id = callback.from_user.id
      user_number = await rq_reg.get_user_number(telegram_id)
      mentor_checker = await rq_link.mentor_or_user(user_number)
      link_public = '<a href=\"https://docs.google.com/document/d/1iDAtecwMIfIhJzXgYadRn12SVIbWvYF_3WMSPJMce0s/edit?usp=sharing\">Открыть инструкцию</a>'
      link_mentor = '<a href=\"https://docs.google.com/document/d/1fmUq3hIMVdEYFQU8_T_TJ_CNLLFteJ6EyDFvccuW55k/edit?usp=sharing\">Открыть инструкцию</a>'
      text_public = (
          f'🛠Теперь поможем тебе разобраться с нашими <b>внутренними процессами.</b>' 
          f'\nДля этого тебе будет полезно ознакомиться с нашей <b>инструкцией,</b> '
          f'которую мы очень трепетно собрали для тебя. Считай её своей шпаргалкой'
          f' по внутренней кухне! Не забывай периодически обращаться к ней\n{link_public}'
      )
      text_mentor = (
          f'Так же тебе, как руководителю отдела, однажды может пригодиться <b>инструкция по подбору персонала</b>. '
          f'\nСохрани её и когда у твоего отдела появится потребность в новом сотруднике, обязательно обратись к '
          f'данной инструкции. {link_mentor}'
      )
      await callback.message.answer(f'{text_public}', reply_markup=kb_start.inline_next_key_nine, parse_mode='HTML')
      if mentor_checker is not None:
          await callback.message.answer(f'{text_mentor}', reply_markup=kb_start.inline_next_key_nine, parse_mode='HTML')

   except Exception as e:
      await callback.message.answer(f"Ошибка: {e}")

@router.callback_query(F.data == 'next_nine')
async def upload_welcomebook(callback: CallbackQuery):
    type_value = 'Welcome book'
    file_link = await rq_link.get_public_files_link(name=type_value)
    link = f'<a href="{file_link}">Welcome Book 🕮</a>'
    text =('Вернёмся к внутренним организационным моментам. ' 
        f'\nДля быстрой адаптации в коллективе мы создали для '
        f'тебя уникальный  {link},  который поможет сориентироваться в первые дни работы.'
        
        )
    text_two = (
        
        f'Отлично, теперь ты подробно изучил наши внутренние регламенты и готов приступить к работе\n'
        f'В заключении давай же узнаем, что тебя ждёт в <b>первый день.</b>'
    )
    if file_link is None:
        await callback.message.answer(f'Файл не найден\n\n{text}', parse_mode='HTML')
    await callback.message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(1.5)
    await callback.message.answer(f'{text_two}', parse_mode='HTML', reply_markup=kb_start.inline_next_key_final)

@router.callback_query(F.data == 'final')
async def final(callback: CallbackQuery):
    text = (
        'Начинаем твой первый рабочий день! 🎉 Чтобы всё прошло гладко, вот наш план:\n\n'
        '\n1. <b>9:30 - Трудоустройство:</b> Встречаемся с HR-менеджером для '
        'оформления всех необходимых документов. Не забудь взять с собой все необходимые документы.'
        '\n2. <b>Экскурсия по офису:</b> Осмотримся, чтобы ты знал, где что находится: кухня, туалет, переговорные комнаты и т.д. 🧭'
        '\n3. <b>Знакомство с командой:</b> Представим тебя коллегам, чтобы ты почувствовал себя частью коллектива! 🤝'
        '\n4. <b>Встреча с непосредственным руководителем:</b> Обсудим задачи на сегодня и на первую неделю, а также ответим на твои вопросы. 🗓️'
        '\n5. <b>Вводное обучение:</b> Познакомим с основными процессами и регламентами, чтобы ты понимал, как всё устроено. 📚'

        '\n\nНадеемся, первый день пройдет продуктивно и интересно! 😉 '
        'Если что-то будет непонятно, смело обращайся к коллегам или руководителю.\n\n'
    )
    await callback.message.answer(f'{text}', parse_mode='HTML')


@router.callback_query(F.data == 'welcome')
async def upload_welcomebook(callback: CallbackQuery):
    type_value = 'Welcome book'
    file_link = await rq_link.get_public_files_link(name=type_value)
    link = f'<a href="{file_link}">Welcome Book 🕮</a>'
    text =('Вернёмся к внутренним организационным моментам. ' 
        f'\nДля быстрой адаптации в коллективе мы создали для '
        f'тебя уникальный  {link},  который поможет сориентироваться в первые дни работы.'
        
        )
    if file_link is None:
        await callback.message.answer(f'Файл не найден\n\n{text}', reply_markup=kb_info.inline_back_info, parse_mode='HTML')
    await callback.message.answer(f'{text}',reply_markup=kb_info.inline_back_info, parse_mode='HTML')

@router.callback_query(F.data == 'reglament_info')
async def regulations(callback: CallbackQuery):
    name = 'Регламент'
    regulations_all = await rq_link.get_regulations_all(name)
    await callback.message.answer(f'А теперь давай углубимся в детали. Чтобы ты мог глубже понять функционал каждого отдела, ' 
                                  'давай-ка изучим <b>регламенты работы каждого отдела</b> 📚. '
                                  'Это поможет тебе разобраться в функционале отделов досконально и подробно объяснит, как всё работает "изнутри".',
                                   reply_markup=kb_start.regulations_all_info(regulations_all), parse_mode='HTML')

@router.callback_query(F.data.startswith('regulation_info|'))
async def uploud_regulation_link(callback: CallbackQuery):
    parts = callback.data.split('|')
    file_id = int(parts[1])
    link = await rq_link.upload_link(file_id)
    await callback.message.answer(f'<a href="{link}">Открыть файл</a>', parse_mode="HTML", reply_markup=kb_start.inline_next_key_eight)