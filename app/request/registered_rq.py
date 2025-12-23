from app.storage.models import async_session
import app.storage.models as db
from sqlalchemy import select, or_
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import asyncio
from main import Bot
import app.onboarding as ops



async def reg_organization(organization_name: str):
    async with async_session() as session:
        registered = await session.scalar(
            select(db.Organization).where(
                db.Organization.organization_name == organization_name
            )
        )
    if registered:
        return False
    organization_new = db.Organization(organization_name=organization_name)
    session.add(organization_new)
    await session.commit()
    return True


async def reg_department(department_name: str, organization_id):
    async with async_session() as session:
        department_name_new = db.Department(
        department_name=department_name, organization_id=organization_id
    )
    session.add(department_name_new)
    await session.commit()
    return True


async def reg_mentor_or_boss(
    name_id, telegram_url, department_id, organization_id, mentor
):
    async with async_session() as session:
        async with session.begin():
            # Получаем пользователя по id
            user = await session.get(db.User, name_id)
            # Обновляем поле username
            user.username = telegram_url
            # Создаем запись в таблице Supervisor
            new_supervisor = db.Supervisor(
                supervisor_id=name_id,
                department_id=department_id,
                organization_id=organization_id,
                mentor=mentor,
            )
            session.add(new_supervisor)
            return True


async def reg_users(department_id: int, number: str, name: str, telegram_id, bot: Bot, state: FSMContext) -> bool:
    async with async_session() as session:
        try:
            result = await session.execute(
                select(db.User).where(
                    or_(db.User.telegram_id == telegram_id,
                        db.User.number == number)
                )
            )
            if result.scalars().first():
                return False

            org_res = await session.execute(
                select(db.Department.organization_id)
                .where(db.Department.id == department_id)
            )
            org_id = org_res.scalar_one_or_none()
            if not org_id:
                return False

            new_user = db.User(
                user_department_id=department_id,
                user_organization_id=org_id,
                name=name,
                number=number,
                telegram_id=telegram_id,
            )

            now = datetime.utcnow()
            history = db.History(
                data_start=now.date().isoformat(),
                data_7=(now + timedelta(days=7)).date().isoformat(),
                data_30=(now + timedelta(days=30)).date().isoformat(),
                data_90=(now + timedelta(days=90)).date().isoformat(),
            )

            new_user.chats.append(history)
            session.add(new_user)
            await session.commit()

            # 🔥 АВТОЗАПУСК ОПРОСОВ (ТЕСТ: 30 СЕК)
            await schedule_polls_for_user(
                user_id=telegram_id,
                bot=bot,
                state=state,
                history=history
            )

            return True

        except Exception as e:
            print(f"Error inserting user: {e}")
            return False

async def schedule_polls_for_user(
    user_id: int,
    bot: Bot,
    history: db.History
):
    """
    Планирует автозапуск опросов для одного пользователя
    (ТЕСТОВЫЙ РЕЖИМ — короткие задержки)
    """

    async def run_poll(poll_type: str, delay: int):
        await asyncio.sleep(delay)  # задержка перед отправкой
        await bot.send_message(user_id, ops.INTRO_TEXTS[poll_type])
        await asyncio.sleep(2)  # маленькая пауза
        await start_poll_without_fsm(user_id, bot, poll_type)

    # 🔴 ТЕСТОВЫЕ ЗАДЕРЖКИ (в секундах)
    asyncio.create_task(run_poll("week1", 1))   # через 1 сек
    asyncio.create_task(run_poll("month1", 10)) # через 10 сек
    asyncio.create_task(run_poll("month3", 30)) # через 30 сек

async def start_poll_without_fsm(user_id: int, bot: Bot, poll_type: str):
    questions = {
        "week1": ops.week1_questions,
        "month1": ops.month1_questions,
        "month3": ops.month3_questions
    }[poll_type]

    # Просто отправляем первый вопрос
    await bot.send_message(user_id, questions[0])

async def restore_schedules(bot: Bot, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(
            select(db.History)
            .join(db.User)
            .where(db.User.telegram_id.isnot(None))
        )

        histories = result.scalars().all()

        for h in histories:
            await schedule_polls_for_user(
                user_id=h.user.telegram_id,
                bot=bot,
                state=state,
                history=h
            )



async def get_all_organization():
    async with async_session() as session:
        result = await session.execute(select(db.Organization))
        return result.scalars().all()


async def get_list_users(dep):
    async with async_session() as session:
        result = await session.execute(
            select(db.User).where(db.User.user_department_id == dep)
        )
        return result.scalars().all()


async def get_all_department(org):
    async with async_session() as session:
        result = await session.execute(
            select(db.Department).where(db.Department.organization_id == org)
        )
        return result.scalars().all()


async def get_all_department_boss(get_org):
    async with async_session() as session:
        result = await session.execute(
            select(db.Department).where(db.Department.organization_id == get_org)
        )
        return result.scalars().all()


async def get_all_organization_name(organization_id):
    async with async_session() as session:
        result = await session.execute(
            select(db.Organization.organization_name).where(
                db.Organization.id == organization_id
            )
        )
        name = result.scalar_one_or_none()
        return name


async def get_user_name(user_number=None, name_id=None):
    async with async_session() as session:
        if name_id is not None:
            result = await session.execute(
                select(db.User.name).where(db.User.id == name_id)
            )
            name = result.scalar_one_or_none()
            return name
        else:
            result = await session.execute(
            select(db.User.name).where(db.User.number == user_number)
            )
            name = result.scalar_one_or_none()
            return name
        


async def get_department_name(department_id):
    async with async_session() as session:
        result = await session.execute(
            select(db.Department.department_name).where(
                db.Department.id == department_id
            )
        )
        name = result.scalar_one_or_none()
        return name


async def check_is_admin(telegram_id: int) -> bool:
    async with async_session() as session:
        admin = await session.scalar(
            select(db.Admin).where(or_
                                   (db.Admin.telegram_id == telegram_id, 
                                    db.Admin.admin_telegram_id == telegram_id)
            )
        )
        return admin is not None


async def reg_new_admin(new_telegram_id, new_pin):
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


async def default_org():
    async with async_session() as session:
        result = await session.execute(select(db.Organization))
        default = result.scalar()
        if not default:
            PMK = db.Organization(organization_name="ПМК")
            GK_PMK = db.Organization(organization_name="ГК ПМК")
            HANGAR = db.Organization(organization_name="ХАНГАР")
            SM = db.Organization(organization_name="СКОЛЬКО?МОЖНО")
            session.add_all([PMK, GK_PMK, HANGAR, SM])
            await session.commit()


async def select_users_department_and_mentor(user_number: int) -> bool:
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
        supervisor_row = await session.scalar(
            select(db.Supervisor.supervisor_id).where(
                (db.Supervisor.department_id == user_department_id)
                & (db.Supervisor.organization_id == user_organization_id)
            )
        )
        supervisor = supervisor_row
        if not supervisor:
            return None
        supervisor_id = supervisor
        supervisor_user = await session.execute(
            select(db.User.name, db.User.username, db.User.number, db.User.id).where(
                db.User.id == supervisor_id
            )
        )
        supervisor_data = supervisor_user.first()
        if not supervisor_data:
            return " ", " ", " ", " ", None
        name, username, number, id = supervisor_data
        return name, username, number, id


async def get_user_name_or_dept(id=None):
    async with async_session() as session:
        result = await session.execute(
            select(db.Department.department_name).where(db.Department.id == id)
        )
        name = result.scalar_one_or_none()
        if not name:
            return " ", None
        return name


async def get_dept_id(user_number):
        async with async_session() as session:
            result = await session.execute(
                select(db.User.user_department_id).where(db.User.number == user_number)
            )
            name = result.scalar_one_or_none()
            return name
        
async def get_user_number(telegram_id):
        async with async_session() as session:
            result = await session.execute(
                select(db.User.number).where(db.User.telegram_id == telegram_id)
            )
            number = result.scalar_one_or_none()
            return number
        
async def get_user_id(number):
        async with async_session() as session:
            result = await session.execute(
                select(db.User.id).where(db.User.number == number)
            )
            user_id = result.scalar_one_or_none()
            return user_id