from app.storage.models import async_session
import app.storage.models as db
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent.parent.parent


async def save_welcome_book(
    file_path: str,
    type: str,
    file_name,
    organization_id=None,
    public_pdf_file=1,
    department_id=None,
):
    async with async_session() as session:
        new_file = db.DepartmentFile(
            name=file_name,
            file_path=file_path,
            type=type,
            public_pdf_file=public_pdf_file,
            department_id=department_id,
            organization_id=organization_id,
            file_size=Path(file_path).stat().st_size,
        )
        session.add(new_file)
        await session.commit()


async def save_videos(file_name: str, file_path: str, type_video):
    async with async_session() as session:
        size = Path(file_path).stat().st_size if Path(file_path).exists() else None
        if isinstance(type_video, int):
            new_file = db.DepartmentFile(
                name=file_name,
                file_path=file_path,
                type="видео отдела",
                department_id=type_video,
                file_size=size,
            )
        elif type_video == 'public':
            new_file = db.DepartmentFile(
                name=file_name,
                file_path=file_path,
                type="публичное видео",
                file_size=size,
            )

        else:
            type_video == 'top_menager'
            new_file = db.DepartmentFile(
                name=file_name,
                file_path=file_path,
                type="Топ менеджера",
                file_size=size,
            )

        session.add(new_file)
        await session.commit()


async def get_organization_name(organization_id):
    async with async_session() as session:
        result = await session.execute(
            select(db.Organization.organization_name).where(
                db.Organization.id == organization_id
            )
        )
        name = result.scalar_one_or_none()
        return name


async def save_sample_link(organization_id, link, name, callback_text=None, dept_id=None):
    async with async_session() as session:
        result = await session.execute(
            select(db.Organization)
            .options(selectinload(db.Organization.departments))
            .where(db.Organization.id == organization_id)
        )
        organization = result.scalar_one_or_none()
        if organization is None:
            return False, f"Организация с id={organization_id} не найдена"

        departments = organization.departments
        if not departments:
            return False, f"У организации id={organization_id} нет отделов"

        department_id = dept_id or departments[0].id

        existing = await session.execute(
            select(db.DepartmentFile).where(db.DepartmentFile.sample_public == link)
        )
        if existing.scalars().first():
            return False, f"Ссылкой '{link}' уже существует"

        allowed_types = (
            "Заявление на отпуск",
            "Заявление на трудоустройство",
            "Заявление об увольнении",
            "Заявление на компенсацию",
            "Заявление на отпуск за свой счет",
            "Служебные записки",
            "Положения (ЛНА)",
            "Информация о ДМС",
            "Добавить приватный файл"
        )
        type_value = callback_text if callback_text in allowed_types else None

        new_sample = db.DepartmentFile(
            organization_id=organization_id,
            department_id=department_id,
            name=name,
            sample_public=link,
            file_path=link,
            type=type_value,
        )
        session.add(new_sample)
        await session.commit()
        return True, "ГОТОВО"


async def get_user_name(user_number):
    async with async_session() as session:
        result = await session.execute(
            select(db.User.id).where(db.User.number == user_number)
        )
        user_name = result.scalar_one_or_none()
        return user_name


async def save_video_link(file_name: str, video_link: str, type_video: str):
    async with async_session() as session:
        try:
            if type_video == 'top_menager':
                video_record = db.DepartmentFile(
                    name=file_name,
                    type='Топ менеджер',
                    file_path=video_link, 
                )
            elif type_video == 'public':
                video_record = db.DepartmentFile(
                    name=file_name,
                    type='публичное видео',
                    file_path=video_link,
                )
            else:
                video_record = db.DepartmentFile(
                    name=file_name,
                    type=type_video,
                    file_path=video_link, 
                )
            session.add(video_record)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении ссылки на видео: {e}")
            return False
    
async def get_file_id_for_dept_name(user):
    async with async_session() as session:
        try:
            dept_id = (await session.execute(select(db.User.user_department_id)
                                             .where(db.User.id == user))).scalar_one_or_none()
            result = await session.execute(select(db.Department.department_name)
                                           .where(db.Department.id == dept_id))
            dept_name = result.scalar_one_or_none()
            return dept_name
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении ссылки на видео: {e}")
            return False

async def get_file_id_for_link_type(dept_name: str):
    async with async_session() as session:

        # Публичное видео
        public_res = await session.execute(
            select(db.DepartmentFile.file_path)
            .where(db.DepartmentFile.type == "публичное видео")
        )
        public_link = public_res.scalar_one_or_none()

        # Видео подразделения
        dept_res = await session.execute(
            select(db.DepartmentFile.file_path)
            .where(db.DepartmentFile.type == dept_name)
        )
        dept_link = dept_res.scalar_one_or_none()

        return dept_link, public_link
    
async def get_public_video(type):
    async with async_session() as session:
        public_link = await session.execute(select(db.DepartmentFile.file_path)
                                       .where(db.DepartmentFile.type == type))
        result = public_link.scalars().all()
        return result

async def get_Dept_name_video(exclude_type: str, user_dept=None):
    allowed_types = (
	'Топ менеджер',
        'Отдел бухгалтерии',
        'Коммерческий отдел',
        'Отдел маркетинга',
        'ОТ и ТБ',
        'Отдел персонала',
        'Отдел снабжения и логистики',
        'Отдел ПТО',
        'Юридический отдел',
        'IT отдел',
        'Административно-управленческий отдел'
    )

    # Если отдел неизвестен → ничего не возвращаем
    if exclude_type not in allowed_types:
        return [], []

    # Если user_dept не передан — считаем его равным exclude_type
    if user_dept is None:
        user_dept = exclude_type

    async with async_session() as session:

        if exclude_type == "Топ менеджер":
            result = await session.execute(
                select(db.DepartmentFile.file_path, db.DepartmentFile.name)
                .where(db.DepartmentFile.type == "Топ менеджер")
            )

        else:
            result = await session.execute(
                select(db.DepartmentFile.file_path, db.DepartmentFile.name)
                .where(db.DepartmentFile.type.in_(allowed_types))
                .where(db.DepartmentFile.type != "Топ менеджер")
                .where(db.DepartmentFile.type != "публичное видео")
                .where(db.DepartmentFile.type != user_dept)  
            )

        rows = result.all()
        print("SQL rows:", rows)

        links = [row[0] for row in rows]
        names = [row[1] for row in rows]

        return links, names

async def get_link(user, file_type):
    async with async_session() as session:
        # Получаем organization_id
        if hasattr(user, "user_organization_id"):
            organization_id = user.user_organization_id
        else:
            result = await session.execute(select(db.User).where(db.User.id == user))
            user_obj = result.scalar_one_or_none()
            if user_obj is None:
                raise ValueError("Пользователь не найден")
            organization_id = user_obj.user_organization_id

        if organization_id is None:
            raise ValueError("Организация не найдена")

        # 1️⃣ Сначала ищем по type
        result_link = await session.execute(
            select(db.DepartmentFile).where(
                and_(
                    db.DepartmentFile.organization_id == organization_id,
                    db.DepartmentFile.type == file_type,
                )
            )
        )
        link_obj = result_link.scalar_one_or_none()

        # 2️⃣ Если не найдено — ищем по name
        if link_obj is None:
            result_link = await session.execute(
                select(db.DepartmentFile).where(
                    and_(
                        db.DepartmentFile.organization_id == organization_id,
                        db.DepartmentFile.name == file_type,
                    )
                )
            )
            link_obj = result_link.scalar_one_or_none()

        if link_obj is None:
            raise ValueError("Файл не найден для данной организации и типа/имени")

        return link_obj.file_path


async def get_link_dms(user, file_type):
    async with async_session() as session:
        if hasattr(user, "user_organization_id"):
            organization_id = user.user_organization_id
        else:
            result = await session.execute(select(db.User).where(db.User.id == user))
            user_obj = result.scalar_one_or_none()
            if user_obj is None:
                raise ValueError("Пользователь не найден")
            organization_id = user_obj.user_organization_id
        if organization_id is None:
            raise ValueError("Организация не найдена")
        result_links = await session.execute(
            select(db.DepartmentFile).where(
                and_(
                    db.DepartmentFile.organization_id == organization_id,
                    db.DepartmentFile.type == file_type,
                )
            )
        )
        files = result_links.scalars().all()
        if not files:
            raise ValueError("Файлы для этой организации не найдены")
        return files


async def get_commission_photo(type_value, organization_id=None, department_id=None):
    async with async_session() as session:
        try:
            query = select(db.DepartmentFile).where(
                db.DepartmentFile.type == type_value
            )
            if organization_id is not None:
                query = query.where(
                    db.DepartmentFile.organization_id == organization_id
                )
            if department_id is not None:
                query = query.where(db.DepartmentFile.department_id == department_id)
            result = await session.execute(query)
            user_objs = result.scalars().all()
            return user_objs
        except Exception as e:
            # Логируем ошибку
            print(f"Ошибка при запросе: {e}")
            return []

        
async def get_sample_type(select_sample_type: str, user_name):
    async with async_session() as session:
        if hasattr(user_name, "user_organization_id"):
            organization_id = user_name.user_organization_id
        else:
            result = await session.execute(
                select(db.User).where(db.User.id == user_name)
            )
            user_obj = result.scalar_one_or_none()
            if user_obj is None:
                raise ValueError("Пользователь не найден")
            organization_id = user_obj.user_organization_id
        if organization_id is None:
            raise ValueError("Организация не найдена")
        result = await session.execute(
            select(db.DepartmentFile).where(
                and_(
                    db.DepartmentFile.type == select_sample_type,
                    db.DepartmentFile.organization_id == organization_id,
                )
            )
        )
        sample_files = result.scalars().all()
        if not sample_files:
            raise ValueError("Файлы с данным типом для организации не найдены")
        return sample_files
    
async def get_file_type(file_id):
    async with async_session() as session:
        file_type = await session.execute(select(db.DepartmentFile.name)
                                       .where(db.DepartmentFile.id == file_id))
        result = file_type.scalar_one_or_none()
        return result
    
async def save_dept_offer(type, name, link):
    async with async_session() as session:
        offer = db.DepartmentFile(
            name = name,
            type = type,
            file_path = link
        )
        session.add(offer)
        await session.commit()
        return True
    
async def get_regulations_all(name):
    async with async_session() as session:
        get_regulations_all = await session.execute(select(db.DepartmentFile)
                                                    .where(db.DepartmentFile.name == name))
        result = get_regulations_all.scalars().all()
        return result
    
async def upload_link(id):
    async with async_session() as session:
        link = await session.execute(select(db.DepartmentFile.file_path)
                                     .where(db.DepartmentFile.id == id))
        return link.scalar_one_or_none()
    
async def mentor_or_user(user_number):
    async with async_session() as session:
        user_id = (await session.execute(select(db.User.id)
                                        .where(db.User.number == user_number
                                               ))).scalar_one_or_none()
        if user_id is None:
            return None
        mentor_id = await session.execute(select(db.Supervisor.supervisor_id)
                                          .where(db.Supervisor.supervisor_id == user_id))
        result = mentor_id.scalar_one_or_none()
        return result

async def get_user_dept(telegram_id):
    async with async_session() as session:
        dept_id = (await session.execute(select(db.User.user_department_id)
                                       .where(db.User.telegram_id == telegram_id)
                                       )).scalar_one_or_none()
        if dept_id is None:
            return None
        
        file_link = await session.execute(select(db.DepartmentFile.file_path)
                                        .where(and_(db.DepartmentFile.type == 'Добавить приватный файл',
                                                    db.DepartmentFile.department_id == dept_id)))
        result = file_link.scalar_one_or_none()
        return result
