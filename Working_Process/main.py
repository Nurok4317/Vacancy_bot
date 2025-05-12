import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
API_TOKEN = ""

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./jobs_bot.db"
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class UserFilter(Base):
    __tablename__ = 'user_filters'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    keywords = Column(String, default='')
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Bot setup
async def main():
    await init_db()

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # /start handler
    @dp.message(Command(commands=['start']))
    async def cmd_start(message: Message):
        await message.answer(
            "Привет! Я бот для поиска вакансий. Многие команды — /add_site, /list_sites, /set_keywords."
        )

    # /add_site handler
    @dp.message(Command(commands=['add_site']))
    async def cmd_add_site(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply("Использование: /add_site <URL>")
            return
        url = parts[1].strip()
        async with async_session() as session:
            exists = await session.scalar(
                session.query(Source).filter_by(url=url).exists()
            )
            if exists:
                await message.reply("Этот источник уже добавлен.")
            else:
                source = Source(url=url)
                session.add(source)
                await session.commit()
                await message.reply(f"Источник {url} успешно добавлен.")

    # /list_sites handler
    @dp.message(Command(commands=['list_sites']))
    async def cmd_list_sites(message: Message):
        async with async_session() as session:
            result = await session.execute(session.query(Source))
            sources = result.scalars().all()
        if not sources:
            await message.reply("Список источников пуст.")
        else:
            text = "Отслеживаемые источники:\n" + "\n".join(
                f"- {s.url} (active={s.active})" for s in sources
            )
            await message.reply(text)

    # start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
