import asyncio
import logging
from aiogram import Dispatcher
from config import bot, dp
import handlers
from database import init_db

async def main():
    try:
        init_db()
        logging.info("Database initialized")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())