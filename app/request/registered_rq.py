from datetime import datetime, timedelta
import asyncio
from sqlalchemy import select, or_, and_, update
from aiogram.fsm.context import FSMContext
from main import Bot

from app.storage.models import async_session
import app.storage.models as db
import app.onboarding as ops


# ====================== Регистрация организации ======================
async def reg_organization(organization_name: str) -> bool:
    async with async_session() as session:
        registered = await session.scalar(
            select(db.Organization).where(db.Organization.organization_name == organization_name)
        )
        if registered:
            return False
        organization_new = db.Organization(organization_name=organization_name)
        session.add(organization_new)
        await session.commit()
        return True


# ====================== Регистрация отдела ======================
async def reg_department(department_name: str, organization_id: int) -> bool:
    async with async_session() as session:
        department_new = db.Department(
            department_name=department_name, organization_id=organization_id
        )
        session.add(department_new)
        await session.commit()
        return True


# ====================== Регистрация наставника или босса ======================
async def reg_mentor_or_boss(
    user_id: int, telegram_url: str, department_id: int, organization_id: int, mentor: bool
) -> bool:
    async with async_session() as session:
        async with session.begin():
            user = await session.get(db.User, user_id)
            if not user:
                return False
            user.username = telegram_url
            supervisor = db.Supervisor(
                supervisor_id=user_id,
                department_id=department_id,
                organization_id=organization_id,
                mentor=mentor,
            )
            session.add(supervisor)
        return True


# ====================== Регистрация пользователя и планировщик ======================
async def reg_users(
    department_id: int, number: str, name: str, telegram_id: int, bot: Bot, state: FSMContext
) -> bool:
    """
    Регистрация нового пользователя и запуск опросов
    """
    async with async_session() as session:
        try:
            print(f"📝 Регистрация пользователя: {name}, telegram_id: {telegram_id}")
            
            # Проверка существующего пользователя
            existing_user = await session.scalar(
                select(db.User).where(
                    (db.User.telegram_id == telegram_id) | (db.User.number == number)
                )
            )
            if existing_user:
                print(f"❌ Пользователь уже существует: {telegram_id}")
                return False

            org_id = await session.scalar(
                select(db.Department.organization_id).where(db.Department.id == department_id)
            )
            if not org_id:
                print(f"❌ Отдел не найден: {department_id}")
                return False

            now = datetime.utcnow()
            new_user = db.User(
                user_department_id=department_id,
                user_organization_id=org_id,
                name=name,
                number=number,
                telegram_id=telegram_id,
            )
            history = db.History(
                data_start=now.date().isoformat(),
                data_7=(now + timedelta(days=7)).date().isoformat(),
                data_30=(now + timedelta(days=30)).date().isoformat(),
                data_90=(now + timedelta(days=90)).date().isoformat(),
            )
            new_user.chats.append(history)
            session.add(new_user)
            await session.commit()

            print(f"✅ Пользователь {telegram_id} успешно зарегистрирован")
            
            # 🔥 Автозапуск опросов
            try:
                # Сначала пытаемся с state
                await ops.schedule_polls_for_user(user_id=telegram_id, bot=bot, state=state)
            except TypeError:
                # Если не принимает state, вызываем без него
                await ops.schedule_polls_for_user(user_id=telegram_id, bot=bot)
                
            return True
        except Exception as e:
            await session.rollback()
            print(f"[reg_users ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False





# ====================== Получение данных ======================
async def get_all_organization():
    async with async_session() as session:
        result = await session.execute(select(db.Organization))
        return result.scalars().all()


async def get_list_users(dep_id: int):
    async with async_session() as session:
        result = await session.execute(select(db.User).where(db.User.user_department_id == dep_id))
        return result.scalars().all()


async def get_all_department(org_id: int):
    async with async_session() as session:
        result = await session.execute(select(db.Department).where(db.Department.organization_id == org_id))
        return result.scalars().all()


async def get_all_organization_name(organization_id: int):
    async with async_session() as session:
        return await session.scalar(
            select(db.Organization.organization_name).where(db.Organization.id == organization_id)
        )


async def get_user_name(user_number: str = None, user_id: int = None, telegram_id: int = None):
    async with async_session() as session:
        if user_id is not None:
            return await session.scalar(select(db.User.name).where(db.User.id == user_id))
        if user_number is not None:
            return await session.scalar(select(db.User.name).where(db.User.number == user_number))
        if telegram_id is not None:
            return await session.scalar(select(db.User.name).where(db.User.telegram_id == telegram_id))
        return None


async def get_department_name(department_id: int):
    async with async_session() as session:
        return await session.scalar(
            select(db.Department.department_name).where(db.Department.id == department_id)
        )


# ====================== Админ функции ======================
async def check_is_admin(telegram_id: int) -> bool:
    async with async_session() as session:
        admin = await session.scalar(
            select(db.Admin).where(
                or_(
                    db.Admin.telegram_id == telegram_id,
                    db.Admin.admin_telegram_id == telegram_id
                )
            )
        )
        return admin is not None


async def reg_new_admin(new_telegram_id: int, new_pin: str) -> bool:
    async with async_session() as session:
        registered = await session.scalar(
            select(db.Admin).where(db.Admin.admin_telegram_id == new_telegram_id)
        )
        if registered:
            return False
        new_admin = db.Admin(admin_telegram_id=new_telegram_id, pin=new_pin)
        session.add(new_admin)
        await session.commit()
        return True


# ====================== Организации по умолчанию ======================
async def default_org():
    async with async_session() as session:  # одна сессия
        # Проверяем, есть ли уже хоть одна организация
        default = await session.scalar(select(db.Organization))
        if not default:
            orgs = [
                db.Organization(organization_name="ПМК"),
                db.Organization(organization_name="ГК ПМК"),
                db.Organization(organization_name=""),  # пустое имя
                db.Organization(organization_name="ХАНГАР"),
                db.Organization(organization_name="СКОЛЬКО?МОЖНО")
            ]
            session.add_all(orgs)
            await session.commit()  # коммитим, чтобы появились id

        # Список департаментов
        departments = [
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
        ]

        # Получаем все организации
        result = await session.execute(select(db.Organization))
        orgs = result.scalars().all()

        for org in orgs:
            for dept_name in departments:
                # Проверяем, есть ли такой департамент
                exists = await session.execute(
                    select(db.Department).where(
                        and_(
                            db.Department.organization_id == org.id,
                            db.Department.department_name == dept_name
                        )
                    )
                )
                if exists.scalars().first():
                    continue  # пропускаем если есть

                # Создаем новый департамент
                new_dept = db.Department(
                    department_name=dept_name,
                    organization_id=org.id
                )
                session.add(new_dept)

        await session.commit()


# ====================== Получение наставника ======================
async def select_users_department_and_mentor(user_number: int):
    async with async_session() as session:
        user_data = await session.execute(
            select(db.User.user_department_id, db.User.user_organization_id).where(
                db.User.number == user_number
            )
        )
        data = user_data.first()
        if not data:
            return None
        user_department_id, user_organization_id = data

        supervisor_id = await session.scalar(
            select(db.Supervisor.supervisor_id).where(
                (db.Supervisor.department_id == user_department_id) &
                (db.Supervisor.organization_id == user_organization_id)
            )
        )
        if not supervisor_id:
            return None

        supervisor_data = await session.execute(
            select(db.User.name, db.User.username, db.User.number, db.User.id).where(db.User.id == supervisor_id)
        )
        supervisor_info = supervisor_data.first()
        if not supervisor_info:
            return " ", " ", " ", " "
        return supervisor_info


# ====================== Другие утилиты ======================
async def get_user_name_or_dept(dept_id: int):
    async with async_session() as session:
        name = await session.scalar(select(db.Department.department_name).where(db.Department.id == dept_id))
        return name or " "


async def get_dept_id(user_number: str):
    async with async_session() as session:
        return await session.scalar(select(db.User.user_department_id).where(db.User.number == user_number))


async def get_user_number(telegram_id: int):
    async with async_session() as session:
        return await session.scalar(select(db.User.number).where(db.User.telegram_id == telegram_id))


async def get_user_id(number: str):
    async with async_session() as session:
        return await session.scalar(select(db.User.id).where(db.User.number == number))

async def check_is_private_files(telegram_id: int):
    async with async_session() as session:
        # Получаем department_id пользователя
        department_id = await session.scalar(
            select(db.User.user_department_id)
            .where(db.User.telegram_id == telegram_id)
        )

        if not department_id:
            return False
        is_private = await session.scalar(
            select(db.Department.private)
            .where(db.Department.id == department_id)
        )

        return is_private


async def save_private(dept_id: int):
    async with async_session() as session: 
        async with session.begin(): 
            result = await session.execute(
                update(db.Department)
                .where(db.Department.id == dept_id)
                .values(private=True)
            )
        if result.rowcount > 0:
            return True  
        else:
            return False 