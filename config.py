from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)