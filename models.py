from sqlalchemy import BigInteger, Sequence
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
import atexit
import datetime

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

atexit.register(engine.dispose)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Sequence('id_sequence', start=1, increment=1), primary_key=True)
    user_id: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    time_start: Mapped[datetime.datetime] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    time_name: Mapped[datetime.datetime] = mapped_column(nullable=True)
    contract: Mapped[str] = mapped_column(nullable=True)
    time_contract: Mapped[datetime.datetime] = mapped_column(nullable=True)
    tube_nick: Mapped[str] = mapped_column(nullable=True)
    time_tube: Mapped[datetime.datetime] = mapped_column(nullable=True)
    vk_nick: Mapped[str] = mapped_column(nullable=True)
    time_vk: Mapped[datetime.datetime] = mapped_column(nullable=True)
    video: Mapped[str] = mapped_column(nullable=True)
    time_video: Mapped[datetime.datetime] = mapped_column(nullable=True)




async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
