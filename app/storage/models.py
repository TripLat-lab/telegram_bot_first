from sqlalchemy import BigInteger, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker,create_async_engine

from pathlib import Path

engine = create_async_engine(url='sqlite+aiosqlite:///storage/db.storage', connect_args={"check_same_thread": False},echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Admin(Base):
    __tablename__="admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    pin: Mapped[str] = mapped_column(String)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger)
    admin_telegram_id: Mapped[int | None] = mapped_column(BigInteger)

class Organization(Base):
    __tablename__="organization"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String(100), unique=True)
    departments: Mapped[list["Department"]] = relationship(back_populates='organization')
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    files: Mapped[list["DepartmentFile"]] = relationship("DepartmentFile", back_populates="organization") 
    supervisors: Mapped[list["Supervisor"]] = relationship("Supervisor", back_populates="organization")

class Department(Base):
    __tablename__="departments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_name: Mapped[str] = mapped_column(String(50))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    organization: Mapped["Organization"] = relationship(back_populates="departments")
    users: Mapped[list["User"]] = relationship(back_populates="department")
    supervisors: Mapped[list["Supervisor"]] = relationship("Supervisor", back_populates="department")
    files: Mapped[list["DepartmentFile"]] = relationship("DepartmentFile", back_populates="department")

class History(Base):
    __tablename__ = 'chat_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="chats")
    data_start: Mapped[str] = mapped_column(nullable=True)
    data_7: Mapped[str] = mapped_column(nullable=True)
    data_30: Mapped[str] = mapped_column(nullable=True)
    data_90: Mapped[str] = mapped_column(nullable=True)
    chat_user: Mapped[str] = mapped_column(nullable=True)
    chat_admin: Mapped[str] = mapped_column(nullable=True)
    chat_data: Mapped[str] = mapped_column(nullable=True)



class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    user_organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    department: Mapped["Department"] = relationship(back_populates="users")
    organization: Mapped["Organization"] = relationship(back_populates="users")
    chats: Mapped[list["History"]] = relationship(
        "History",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    username: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column (String(100), nullable=True)

class DepartmentFile(Base):
    __tablename__ = "samples"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    public_pdf_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    sample_public: Mapped[str] = mapped_column(String, default=False, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=True)
    department: Mapped["Department"] = relationship(back_populates="files")
    organization: Mapped["Organization"] = relationship(back_populates="files")
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=True)
    part_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

class Supervisor(Base):
    __tablename__ = 'supervisor'
    id: Mapped[int] = mapped_column(primary_key=True)
    mentor: Mapped[int] = mapped_column(String, default='No', nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=True)
    department: Mapped["Department"] = relationship("Department", back_populates="supervisors")
    organization: Mapped["Department"] = relationship("Organization", back_populates="supervisors")
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)


def get_full_path(self, base_dir: Path) -> Path:
    return base_dir / self.file_path


def init_admin_data(session: Session):
    if not session.query(Admin).first():
        admin = Admin(pin="1234", telegram_id=310416402, admin_telegram_id=310416402)
        session.add(admin)
        session.commit()




async def async_main():
    storage_dir = Path("storage")
    storage_dir.mkdir(exist_ok=True, parents=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


