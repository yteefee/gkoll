from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)