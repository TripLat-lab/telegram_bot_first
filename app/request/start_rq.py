from app.storage.models import async_session
import app.storage.models as db
from sqlalchemy import select, or_


async def check_number(normalized_number: str):
    async with async_session() as session:
        user = await session.scalar(select(db.User).where(db.User.number == normalized_number))
        return user is not None
    
async def reg_adm(pin: str, telegram_id: int) -> bool:
    async with async_session() as session:
        existing_pin = await session.scalar(
            select(db.Admin).where(db.Admin.pin == pin)
        )
        if existing_pin:
            return False
        existing_admin = await session.scalar(
            select(db.Admin).where(
                or_(
                    db.Admin.telegram_id == telegram_id,
                    db.Admin.admin_telegram_id == telegram_id
                )
            )
        )
        if existing_admin:
            existing_admin.pin = pin
            session.add(existing_admin) 
        else:
            new_admin = db.Admin(pin=pin, telegram_id=telegram_id, admin_telegram_id=telegram_id)
            session.add(new_admin)
        await session.commit()
        return True
   
async def check_password(password: str) -> bool:
    async with async_session() as session:
        admin = await session.scalar(select(db.Admin).where(db.Admin.pin == password))
        return admin is not None
    
async def get_name_user(normalized_number):
    async with async_session() as session:
        user = await session.scalar(select(db.User).where(db.User.number == normalized_number))
        return user.name
    
async def init_admin_data():
    async with async_session() as session:
        result = await session.execute(select(db.Admin))
        admin_exists = result.scalar()
        if not admin_exists:
            admin = db.Admin(pin = 2222, telegram_id = 950860793)
            session.add(admin)
            await session.commit() 