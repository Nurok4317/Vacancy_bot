import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import StateFilter


from sqlalchemy import select

from db import engine, Base, async_session
from models import Source
from registration import (
    handle_start_command, handle_register, handle_authorize,
    process_full_name, process_username, process_password,
    process_login_tgid, process_login_password,
    RegisterForm, LoginForm
)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация БД
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()

    bot = Bot(token="8112532328:AAGh4RgUwkNXpoGdZhvZV7Q3m4kMt0R3QzA")
    dp = Dispatcher(storage=MemoryStorage())

    # /start и кнопки
    dp.message.register(handle_start_command, Command("start"))
    dp.callback_query.register(handle_register, F.data == "register")
    dp.callback_query.register(handle_authorize, F.data == "authorize")

    # Регистрация через FSM: теперь с явным StateFilter
    dp.message.register(process_full_name, StateFilter(RegisterForm.full_name))
    dp.message.register(process_username, StateFilter(RegisterForm.username))
    dp.message.register(process_password, StateFilter(RegisterForm.password))

    # Авторизация через FSM
    dp.message.register(process_login_tgid, StateFilter(LoginForm.telegram_id))
    dp.message.register(process_login_password, StateFilter(LoginForm.password))
    # Примеры остальных команд
    @dp.message(Command("add_site"))
    async def cmd_add_site(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply("Использование: /add_site <URL>")
        url = parts[1].strip()
        async with async_session() as session:
            result = await session.execute(select(Source).where(Source.url == url))
            if result.scalar_one_or_none():
                await message.reply("Этот источник уже добавлен.")
            else:
                session.add(Source(url=url))
                await session.commit()
                await message.reply(f"Источник {url} успешно добавлен.")

    @dp.message(Command("list_sites"))
    async def cmd_list_sites(message: Message):
        async with async_session() as session:
            result = await session.execute(select(Source))
            sources = result.scalars().all()
        if not sources:
            return await message.reply("Список источников пуст.")
        lines = [f"- {s.url} (active={s.active})" for s in sources]
        await message.reply("Отслеживаемые источники:\n" + "\n".join(lines))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
