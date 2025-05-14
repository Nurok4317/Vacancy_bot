from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from db import async_session
from models import User

# Состояния регистрации и логина
class RegisterForm(StatesGroup):
    full_name = State()
    username = State()
    password = State()

class LoginForm(StatesGroup):
    telegram_id = State()
    password = State()

# Клавиатура старта
start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🆕 Регистрация", callback_data="register")],
    [InlineKeyboardButton(text="🔐 Авторизация", callback_data="authorize")],
])
async def handle_start_command(message: Message):
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=start_kb)

# Регистрация
async def handle_register(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваше ФИО:")
    await state.set_state(RegisterForm.full_name)
    await callback.answer()

async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer("Введите ваш никнейм:")
    await state.set_state(RegisterForm.username)

async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("Придумайте пароль:")
    await state.set_state(RegisterForm.password)

async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        user = User(
            telegram_id=message.from_user.id,
            full_name=data["full_name"],
            username=data["username"],
            password=message.text.strip(),
            is_authorized=True
        )
        session.add(user)
        await session.commit()
    await message.answer("✅ Регистрация прошла успешно!")
    await state.clear()

# Авторизация
async def handle_authorize(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваш Telegram ID:")
    await state.set_state(LoginForm.telegram_id)
    await callback.answer()

async def process_login_tgid(message: Message, state: FSMContext):
    await state.update_data(tgid=message.text.strip())
    await message.answer("Введите пароль:")
    await state.set_state(LoginForm.password)

async def process_login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        tgid = int(data["tgid"])
    except ValueError:
        await message.answer("❌ Неверный формат Telegram ID.")
        await state.clear()
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == tgid,
                User.password == message.text.strip()
            )
        )
        user = result.scalar_one_or_none()
        if user:
            user.is_authorized = True
            await session.commit()
            await message.answer("✅ Авторизация успешна!")
        else:
            await message.answer("❌ Неверный Telegram ID или пароль.")
    await state.clear()
