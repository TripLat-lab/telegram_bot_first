from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
import logging
import time

import app.keyboard.file.sample_kb as kb_sample
import app.keyboard.start_kb as kb_user
import app.keyboard.admin_kb as kb_admin
import app.state.start_st as st
import app.request.registered_rq as rq_reg
import app.request.link_files.sample_link_file_rq as rq_link


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "back_sample_admin")
async def back_sample_admin(callback: CallbackQuery):
    await callback.message.answer(
        "Начально меню", reply_markup=kb_sample.inline_add_doc_file
    )


@router.message(F.text == "Администрирование файлов")
async def select_file_type(message: Message):
    await message.answer(
        "Выберите действие", reply_markup=kb_sample.inline_add_doc_file
    )


@router.callback_query(F.data == "add_keyboards_sample_holiday")
async def select_holiday_type(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите тип файлов", reply_markup=kb_sample.inline_select_holiday
    )


@router.callback_query(F.data == "add_sample")
async def select_type_file(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Выберите образец заявления", reply_markup=kb_sample.inline_select_doc_files
    )


@router.callback_query(
    F.data.in_(
        [
            "add_sample_holiday",
            "get_A_job",
            "out_a_job",
            "add_money",
            "add_no_money",
            "Internal_memo",
            "add_offers",
            "add_private_files"
        ]
    )
)
async def organization_for_simple(callback: CallbackQuery, state: FSMContext):
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    await state.update_data(callback_data=callback.data, button_text=button_text)
    org_select = await rq_reg.get_all_organization()
    if callback.data == 'add_private_files':
        await callback.message.answer(
            "Выберите организацию для добавления ",
            reply_markup=kb_sample.select_sample_org(org_select, prefix="org_private"),
        )
        await state.set_state(st.upload_link_files_sample.select_org_sample)
    else:
        await callback.message.answer(
            "Выберите организацию для добавления ",
            reply_markup=kb_sample.select_sample_org(org_select, prefix="org_select"),
        )
        await state.set_state(st.upload_link_files_sample.select_org_sample)


@router.callback_query(F.data.startswith(("org_select", "org_private"))) 
async def select_user_department(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("org_private"):
        parts = callback.data.split("|")
        if len(parts) != 2:
            await callback.answer("Такой оргазиции не существует", show_alert=True)
            return
        organization_id = int(parts[1])
        dept_id = await rq_reg.get_all_department(organization_id)
        await callback.message.answer("Выберите отдел куда добавить файл",
                                      reply_markup=kb_sample.select_sample_dept(departments=dept_id, prefix="private"))
        await state.update_data(organization_id=organization_id)
        organization_name = await rq_link.get_organization_name(organization_id)
    else:
        parts = callback.data.split("|")
        if len(parts) != 2:
            await callback.answer("Такой оргазиции не существует", show_alert=True)
            return
        
        organization_id = int(parts[1])
        await state.set_state(st.upload_link_files_sample.select_org_sample)
        await state.update_data(organization_id=organization_id)
        organization_name = await rq_link.get_organization_name(organization_id)
        await callback.answer()
        await callback.message.answer(
            f"Выбрана организация: {organization_name}" f"\nОтпрвьте название документа",
            reply_markup=kb_sample.back_menu_sample,
        )


@router.callback_query(F.data.startswith(("private"))) 
async def select_user_dept_for_private(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    dept_id = int(parts[1])
    await state.set_state(st.upload_link_files_sample.select_dept_sample)
    await state.update_data(dept_id=dept_id)
    organization_name = await rq_reg.get_department_name(dept_id)
    await callback.message.answer(
        f"Выбрана организация: {organization_name}" f"\nОтпрвьте название документа",
        reply_markup=kb_sample.back_menu_sample,
    )


@router.message(StateFilter (st.upload_link_files_sample.select_org_sample,
                             st.upload_link_files_sample.select_dept_sample))
async def upload_link_sample(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"файл: {message.text}" f"\nОтправьте ссылку на google doc",
        reply_markup=kb_sample.back_menu_sample,
    )
    await state.set_state(st.upload_link_files_sample.upload_link)


@router.message(st.upload_link_files_sample.upload_link)
async def confirmation_sample_file(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    type = data.get("button_text")
    organization_id = data.get("organization_id")
    name = data.get("name")
    link = data.get("link")
    dept_id = data.get('dept_id')
    dept_name = await rq_reg.get_department_name(dept_id)
    org = await rq_link.get_organization_name(organization_id)
    if dept_id is None:
        await message.answer(
            f"Тип файла: '{type}'"
            f"\nОрганизация: '{org}'"
            f"\nНазвание файла: '{name}'"
            f"\nСсылка на файл: <a href='{link}'>Ссылка</a>",
            parse_mode="HTML",
            reply_markup=kb_sample.inline_add_sample,
            disable_web_page_preview=True
        )
    else:
        await message.answer(
            f"Тип файла: '{type}'"
            f"\nОрганизация: '{org}'"
            f"\nНазвание файла: '{name}'"
            f"\nОтдел: {dept_name}"
            f"\nСсылка на файл: <a href='{link}'>Ссылка</a>",
            parse_mode="HTML",
            reply_markup=kb_sample.inline_add_sample,
            disable_web_page_preview=True
        )


@router.callback_query(F.data.in_(["ok_sample", "no_sample"]))
async def save_sample(callback: CallbackQuery, state: FSMContext):
    if callback.data == "ok_sample":
        data = await state.get_data()
        organization_id = data.get("organization_id")
        name = data.get("name")
        link = data.get("link")
        dept_id = data.get('dept_id')
        callback_text = data.get("button_text")
        if not all([organization_id, link, name]):
            await callback.message.answer(
                "Ошибка: Не все необходимые данные были переданы"
            )
            await state.finish()
            return
        success, result = await rq_link.save_sample_link(
            organization_id, link, name, callback_text, dept_id
        )
        if success:
            await callback.message.answer(
                f"Ссылка на образец документа добавлена!\n {name}",
                reply_markup=kb_admin.Menu_admin,
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(f"Ошибка: {result}")
        await state.finish()


@router.callback_query(F.data == "back_sample_user")
async def back_sample_user(callback: CallbackQuery):
    await callback.message.answer("Выберите действие", reply_markup=kb_user.Menu_user)


@router.message(F.text == "Документы и бланки")
async def offers_and_simple(message: Message):
    await message.answer(
        "Выберите нужный пункт", reply_markup=kb_sample.inline_offers_and_simple
    )


@router.callback_query(F.data == "sample")
async def select_type_file(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Выберите образец заявления",
        reply_markup=kb_sample.inline_select_doc_files_for_user,
    )


@router.callback_query(F.data == "reference")
async def select_type_file(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Какая справка нужна", reply_markup=kb_sample.inline_reference_hr_and_buh
    )


@router.callback_query(F.data == "sample_holiday")
async def select_holiday_type_user(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите тип отпуска", reply_markup=kb_sample.inline_select_holiday_users
    )


@router.callback_query(
    F.data.in_(
        [
            "get_A_job_user",
            "out_a_job_user",
            "add_money_user",
            "add_sample_holiday_users",
            "add_no_money_user",
            "Internal_memo_user",
            "offers",
        ]
    )
)
async def select_type_sample(callback: CallbackQuery, state: FSMContext):
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    await state.update_data(sample_type=button_text)
    await state.set_state(st.upload_link_files_sample.get_type)
    data = await state.get_data()
    select_sample_type = data.get("sample_type")
    telegram_id = callback.from_user.id
    user_number = await rq_reg.get_user_number(telegram_id)
    user_id = await rq_reg.get_user_id(user_number)
    select_type_sample_user = await rq_link.get_sample_type(
        select_sample_type, user_id
    )
    if callback.data == 'offers':
        await callback.message.answer(
            "выберите нужный файл",
            reply_markup=kb_sample.select_sample_for_user(select_type_sample_user),
        )
    link_odj = await rq_link.get_link(user_id, select_sample_type)
    await callback.message.answer(
        f'<a href="{link_odj}">Открыть файл</a>', parse_mode="HTML"
    )




@router.callback_query(F.data.startswith("select_type_sample_user|"))
async def select_organization(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    file_id = int(parts[1])
    file_type = await rq_link.get_file_type(file_id)
    telegram_id = callback.from_user.id
    user_number = await rq_reg.get_user_number(telegram_id)
    user_id = await rq_reg.get_user_id(user_number)
    link_odj = await rq_link.get_link(user_id, file_type)
    await callback.message.answer(
        f'<a href="{link_odj}">Открыть файл</a>', parse_mode="HTML"
    )



@router.callback_query(F.data == "add_pdf")
async def add_pdf(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите куда добавить файл", reply_markup=kb_sample.inline_add_pdf_file
    )


@router.callback_query(F.data.in_(["GK_PDF", "welcome_book", "compony_info"]))
async def save_pdf_file(callback: CallbackQuery, state: FSMContext):
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    await state.update_data(upload_pdf=button_text)
    await callback.message.answer(
        "Отправьте PDF-файл велкомбука", reply_markup=kb_sample.back_menu_sample
    )
    await state.set_state(st.add_pdf.upload_pdf)
    await callback.answer()


@router.message(
    F.document.mime_type == "application/pdf", StateFilter(st.add_pdf.upload_pdf)
)
async def handle_pdf_upload(message: Message, state: FSMContext):
    data = await state.get_data()
    description = data.get("upload_pdf")
    try:
        upload_dir = rq_link.BASE_DIR / "storage/pdf-files"
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / message.document.file_name
        try:
            file = await message.bot.get_file(message.document.file_id)
            file_path_tg = file.file_path
            file_name = message.document.file_name
            await message.bot.download_file(file_path_tg, destination=file_path)
        except Exception as download_error:
            await message.answer("Ошибка при скачивании файла")
            print(f"Ошибка скачивания: {download_error}")
            return
        if file_path.stat().st_size == 0:
            await message.answer("Файл пустой")
            file_path.unlink()
            return
        await rq_link.save_welcome_book(
            file_path=str(file_path.relative_to(rq_link.BASE_DIR)),
            type=description,
            file_name=file_name,
        )
        await message.answer("Документ успешно сохранен")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.callback_query(F.data.in_(["company_structure", "dms_info"]))
async def select_org_pdf(callback: CallbackQuery, state: FSMContext):
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    await state.update_data(PDF_type=button_text)
    organization = await rq_reg.get_all_organization()
    await callback.message.answer(
        "Выберите организацию",
        reply_markup=kb_sample.select_video_org(organization, prefix="org_pdf"),
    )


@router.callback_query(F.data.startswith("org_pdf"))
async def select_org_pdf(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    org = int(parts[1])
    await state.update_data(organization_id=org)
    await state.set_state(st.add_pdf.add_pdff)
    await callback.message.answer(f"Отправьте ПДФ файл для отдела")


@router.message(
    F.document.mime_type == "application/pdf", StateFilter(st.add_pdf.add_pdff)
)
async def handle_pdf_org_upload(message: Message, state: FSMContext):
    data = await state.get_data()
    org = data.get("organization_id")
    description = data.get("PDF_type")
    try:
        upload_dir = rq_link.BASE_DIR / "storage/pdf-files"
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / message.document.file_name
        try:
            file = await message.bot.get_file(message.document.file_id)
            file_path_tg = file.file_path
            file_name = message.document.file_name
            await message.bot.download_file(file_path_tg, destination=file_path)
        except Exception as download_error:
            await message.answer("Ошибка при скачивании файла")
            print(f"Ошибка скачивания: {download_error}")
            return
        if file_path.stat().st_size == 0:
            await message.answer("Файл пустой")
            file_path.unlink()
            return
        await rq_link.save_welcome_book(
            file_path=str(file_path.relative_to(rq_link.BASE_DIR)),
            type=description,
            file_name=file_name,
            organization_id=org,
            public_pdf_file=None,
        )
        await message.answer("Документ успешно сохранен")
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.callback_query(F.data == "add_videos")
async def start_add_videos(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите тип добавляемового видео",
        reply_markup=kb_sample.inline_add_video_file,
    )

@router.callback_query(F.data.in_(["public_videos", "department_videos", "top_menedment"]))
async def select_type_videos(callback: CallbackQuery, state: FSMContext):
    if callback.data in ["public_videos", "top_menedment"]:
        await callback.message.answer(
            "Отправьте ссылку на видео (RUTube, VK, или прямую ссылку на видеофайл)"
        )
        await state.set_state(st.type_videos.type_video)
        if callback.data == "public_videos":
            await state.update_data(type_video="public")
            return
        elif callback.data == "top_menedment":
            await state.update_data(type_video="top_menager")
            return
    else:
        org_videos = await rq_reg.get_all_organization()
        await callback.message.answer(
            "Выберите организацию куда добавить видео",
            reply_markup=kb_sample.select_video_org(org_videos, prefix="org_videos"),
        )
        return


@router.callback_query(F.data.startswith("org_videos"))
async def select_department_videos(callback: CallbackQuery):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    org = int(parts[1])
    video_dept = await rq_reg.get_all_department(org)
    await callback.message.answer(
        "Выберите отдел куда нужно добавить видео",
        reply_markup=kb_sample.select_dept_videos(video_dept, prefix="video_dept"),
    )


@router.callback_query(F.data.startswith("video_dept"))
async def upload_dept_videos(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    department_id = int(parts[1])
    department_name = await rq_reg.get_department_name(department_id)
    await state.update_data(department_name=department_name, type_video=department_name)
    await state.set_state(st.type_videos.type_video)
    await callback.message.answer(
        "Отправьте ссылку на видео (RUTube, VK, или прямую ссылку на видеофайл)"
    )

@router.message(F.text, StateFilter(st.type_videos.type_video))
async def get_name_video(message: Message, state: FSMContext):
    video_link = message.text.strip()
    if not video_link.startswith(('http://', 'https://')):
        await message.answer("Пожалуйста, отправьте корректную ссылку (должна начинаться с http:// или https://)")
        return
    await message.answer('Введите описание')
    name = message.text.strip()
    await state.update_data(video_link = video_link)
    await state.set_state(st.type_videos.name)


@router.message(F.text, StateFilter(st.type_videos.name))
async def handle_video_link_upload(message: Message, state: FSMContext):
    name = message.text.strip()

    data = await state.get_data()
    department_name = data.get("department_name")
    type_video = data.get("type_video")
    video_link = data.get('video_link')


    department_info = (
        "Видео будет доступно всем отделам"
        if type_video == "public" or type_video == 'top_menager'
        else (
            f"Видео будет сохранено в отдел: {department_name}"
            if department_name and isinstance(type_video, int)
            else "Видео будет публичным!"
        )
    )
    
    await state.update_data(
        video_link=video_link, 
        type_video=type_video,
        name = name
    )
 
    
    await message.answer(
        f"Подтвердите сохранение видео:\n"
        f"Ссылка: {video_link}\n"
        f"{department_info}\n"
        f"{name}",
        reply_markup=kb_sample.yes_no_keyboard_video_add,
    )
    await state.set_state(st.type_videos.upload_link_videos)


@router.callback_query(F.data == "ok_video", StateFilter(st.type_videos.upload_link_videos))
async def save_video_link(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        type_video_value = data.get("type_video")
        video_link = data.get("video_link")
        file_name = data.get('name')

        # Сохраняем ссылку в базу данных
        await rq_link.save_video_link(file_name, video_link, type_video_value)
        
        await callback.message.answer("Ссылка на видео успешно сохранена!")
        await state.clear()
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при сохранении: {e}")
        await state.clear()


@router.callback_query(F.data == "cancel_video", StateFilter(st.type_videos.upload_link_videos))
async def cancel_video_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Загрузка видео отменена")
    await state.clear()

@router.callback_query(F.data == 'department_offer')
async def seleckt_depart_offer(callback: CallbackQuery, state: FSMContext):
    org_select = await rq_reg.get_all_organization()
    await callback.message.answer(
        "Выберите организацию для добавления ",
        reply_markup=kb_sample.select_sample_org(org_select, prefix="org_offer"),
    )
@router.callback_query(F.data.startswith("org_offer"))
async def select_department_offer(callback: CallbackQuery):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    org = int(parts[1])
    offer_dept = await rq_reg.get_all_department(org)
    await callback.message.answer(
        "Выберите отдел куда нужно добавить регламент",
        reply_markup=kb_sample.select_dept_videos(offer_dept, prefix="offer_dept")
    )
@router.callback_query(F.data.startswith('offer_dept'))
async def input_offer_name(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    dept_id = int(parts[1])
    department_name = await rq_reg.get_department_name(dept_id)
    dept_name = 'Регламент ' + department_name
    state.update_data(deparment_name=dept_name)
    await callback.message.answer(f'Отправьте ссылку на документ')
    await state.update_data(dept_name=dept_name)
    await state.set_state(st.upload_link_files_sample.link)


@router.message(F.text, StateFilter(st.upload_link_files_sample.link))
async def handle_dept_link_upload(message: Message, state: FSMContext):
    video_link = message.text.strip()
    # Простая валидация ссылки
    if not video_link.startswith(('http://', 'https://')):
        await message.answer("Пожалуйста, отправьте корректную ссылку (должна начинаться с http:// или https://)")
        return
    data = await state.get_data()
    video_link = video_link
    type = data.get('dept_name')
    name = 'Регламент'
    await rq_link.save_dept_offer(type, name, video_link)
    await message.answer('Сохранено!')

@router.callback_query(F.data == 'motivation')
async def get_private_files(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    file_link = await rq_link.get_user_dept(telegram_id)
    if not file_link:
        await callback.message.answer("Данная кнопка находить в разработке")
    else:
        await callback.message.answer(f'<a href=\"{file_link}\">Открыть файл</a>',
                                      parse_mode='HTML')
