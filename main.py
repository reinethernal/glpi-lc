import os
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import register_handlers
import logging

logging.basicConfig(level=logging.DEBUG)  # Установка уровня логирования

load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
bot = Bot(token=TELEGRAM_API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers(dp)  # Передача Dispatcher в функцию регистрации обработчиков

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
