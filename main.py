import asyncio
from aiogram import Dispatcher
from config import bot, dp
import handlers
from database import init_db

async def main():
    init_db()  # Инициализация базы данных
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())