from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaDocument
from aiogram.filters import StateFilter
from aiogram import F, Router
import app.request.link_files.sample_link_file_rq as rq_link
import app.request.registered_rq as rq_reg
from aiogram.fsm.context import FSMContext
import logging
import asyncio
import app.state.start_st as st

import app.keyboard.total_ifo_kb as kb_info
import app.keyboard.file.sample_kb as kb_file



router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == 'photo')
async def select_photo_type (callback: CallbackQuery):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    await callback.message.answer('Выберите какую фотографию добавить', reply_markup=kb_file.inline_image)

@router.callback_query(F.data.in_(['medical_dept', 'medical_logo', 'medical', 'org']))
async def select_photo_commission(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    button_text = None
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback.data:
                button_text = button.text
                break
    await state.update_data(type = button_text)
    await state.set_state(st.add_photo.add_photo)
    await callback.message.answer(f'Отправьте изображение')
@router.message(F.content_type.in_({'photo'}), StateFilter(st.add_photo.add_photo))
async def save_photo_commission(message: Message, state: FSMContext):
    data = await state.get_data()
    type = data.get('type')
    organization_id = data.get('organization_id')
    department_id = data.get('department_id')
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_name = f"photo_{file_id}.jpg"
        file_size = photo.file_size
        try:
            upload_dir = rq_link.BASE_DIR / 'storage/photo'
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_info = await message.bot.get_file(file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)
            file_path = upload_dir / file_name  
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())
        except Exception as download_error:
            await message.answer("Ошибка при скачивании файла")
            print(f"Ошибка скачивания: {download_error}")
            return  
        if file_path.stat().st_size == 0:
            await message.answer("Файл пустой")
            file_path.unlink() 
            return
        await rq_link.save_welcome_book(
            file_path = str(file_path.relative_to(rq_link.BASE_DIR)),
            type = type,
            file_name = file_name,
            department_id=department_id,
            organization_id=organization_id,
            public_pdf_file=None)
        await message.answer("Документ успешно сохранен")
    else:
        await message.answer("Не удалось обработать файл")

@router.callback_query(F.data.in_(['logo', 'navigator']))
async def select_type_photo_org_or_dept(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    admin_accept = await rq_reg.check_is_admin(telegram_id)
    if not admin_accept:
        await callback.message.answer(" У вас нет прав для выполнения этой команды")
        return
    organization = await rq_reg.get_all_organization() 
    await callback.message.answer('Выберите организацию', reply_markup=kb_file.select_sample_org(organization, prefix='org_photo'))
@router.callback_query(F.data.startswith('org_photo'))
async def select_type_photo_org(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) !=2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    org = int(parts[1])
    await state.update_data(organization_id = org)
    await callback.message.answer('Выберите это для отдела или организации', reply_markup=kb_file.inline_image_dept_or_org)
@router.callback_query(F.data == 'photo_dept')
async def select_type_photo_dept(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    org = data.get ('organization_id')
    video_dept = await rq_reg.get_all_department(org)
    await callback.message.answer("Выберите отдел куда нужно добавить файл", reply_markup=kb_file.select_dept_videos(video_dept, prefix='photo_dept'))
@router.callback_query(F.data.startswith("photo_dept"))
async def upload_dept_photo(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("|")
    if len(parts) != 2:
        await callback.answer("Такой оргазиции не существует", show_alert=True)
        return
    department_id = int(parts[1])
    department_name = await rq_reg.get_department_name(department_id)
    await state.update_data(department_id = department_id)
    await callback.message.answer(f'Выбрали отдела {department_name}', reply_markup=kb_file.inline_image_dept_or_org)