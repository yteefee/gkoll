from aiogram import F, types
from aiogram.filters import Command
import random
from database import add_user, add_message, get_stats
from config import dp
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Прикольные фишки
JOKES = {
    "stats": [
        "Я слежу за тобой...",
        "Ты в моей базе!",
        "Статистика - это скучно, но вот:"
    ],
    "number": [
        ("🎉 {}! Да ты везунчик!", (90, 100)),
        ("😢 {}... Не повезло...", (1, 10)),
        ("Твое число: {}", (10, 90))
    ],
    "facts": [
        "Кряканье утки не создает эха!",
        "У медуз нет мозга!",
        "Сердце креветки в голове!"
    ],
    "wisdoms": [
        "Если проблема решается деньгами - это расходы",
        "Лучше сделать и пожалеть, чем не сделать",
        "Утро начинается с осознания, что ты проснулся"
    ]
}

def build_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📊 Статистика"))
    builder.add(types.KeyboardButton(text="🎲 Рандомное число"))
    builder.add(types.KeyboardButton(text="🤪 Случайный факт"))
    builder.add(types.KeyboardButton(text="💡 Мудрость дня"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        "🤪 <b>CrazyBot активирован!</b>\n\n"
        "Кнопки работают! Пробуй:\n"
        "- 📊 Статистика\n"
        "- 🎲 Рандом\n"
        "- 🤪 Факт\n"
        "- 💡 Мудрость",
        parse_mode="HTML",
        reply_markup=build_keyboard()
    )

@dp.message(F.text.in_(["📊 Статистика", "/stats"]))
async def stats(message: types.Message):
    stats = get_stats()
    await message.answer(
        f"{random.choice(JOKES['stats'])}\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых сегодня: {stats['new_users_today']}\n"
        f"✉️ Всего сообщений: {stats['total_messages']}\n"
        f"💬 Активных сегодня: {stats['active_today']}",
        reply_markup=build_keyboard()
    )

@dp.message(F.text.in_(["🎲 Рандомное число", "/random"]))
async def random_num(message: types.Message):
    num = random.randint(1, 100)
    for response, (min_, max_) in JOKES['number']:
        if min_ <= num <= max_:
            await message.answer(response.format(num), reply_markup=build_keyboard())
            break

@dp.message(F.text.in_(["🤪 Случайный факт", "/fact"]))
async def fact(message: types.Message):
    await message.answer(
        f"🤓 <b>Факт:</b>\n{random.choice(JOKES['facts'])}",
        parse_mode="HTML",
        reply_markup=build_keyboard()
    )

@dp.message(F.text.in_(["💡 Мудрость дня", "/wisdom"]))
async def wisdom(message: types.Message):
    await message.answer(
        f"🧠 <b>Мудрость:</b>\n{random.choice(JOKES['wisdoms'])}",
        parse_mode="HTML",
        reply_markup=build_keyboard()
    )

@dp.message(F.text)
async def text(message: types.Message):
    add_message(message.from_user.id, message.text)
    await message.answer(
        random.choice(["✅ Запомнил!", "📝 Записал!", "👌 Готово!"]),
        reply_markup=build_keyboard()
    )