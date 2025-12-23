from app.storage.models import async_session
import app.storage.models as db
from sqlalchemy import select, or_
from sqlalchemy import DateTime
from datetime import datetime, timedelta

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


async def reg_users(department_id: int, number: str, name: str, telegram_id) -> bool:
    async with async_session() as session:
        try:
            # ищем, есть ли пользователь с таким telegram_id или number
            result = await session.execute(
                select(db.User).where(
                    or_(db.User.telegram_id == telegram_id,
                        db.User.number == number)
                )
            )
            existing_user = result.scalars().first()
            if existing_user is not None:
                # пользователь уже есть — прекращаем
                return False

            # иначе — получаем org_id
            org_res = await session.execute(
                select(db.Department.organization_id)
                .where(db.Department.id == department_id)
            )
            org_id = org_res.scalar_one_or_none()
            if org_id is None:
                return False
            
            new_user = db.User(
                user_department_id=department_id,
                user_organization_id=org_id,
                name=name,
                number=number,
                telegram_id=telegram_id,
            )
            data_start = datetime.utcnow().date()
            data_two = data_start + timedelta(minutes=7)
            data_three = data_start + timedelta(minutes=30)
            data_four = data_start + timedelta(minutes=90)
            history = db.History(
                data_start=data_start.isoformat(),
                data_7=data_two.isoformat(),
                data_30=data_three.isoformat(),
                data_90=data_four.isoformat()
            )
            new_user.chats.append(history)
            session.add(new_user)
            await session.commit()
            return True

        except Exception as e:
            print(f"Error inserting user: {e}")
            # можно session.rollback() при ошибке
            return False


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