import os
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from dotenv import load_dotenv
from handlers import register_handlers
import logging
import pymongo

logging.basicConfig(level=logging.DEBUG)  # Set logging level

load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')  # MongoDB connection string
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')  # MongoDB database name
MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME')  # MongoDB collection name

# Connect to MongoDB and initialize storage for the bot
client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
db = client.get_database(MONGO_DB_NAME)
storage = MongoStorage(db=db, collection=MONGO_COLLECTION_NAME)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot, storage=storage)

register_handlers(dp)  # Register handlers with the dispatcher

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
