import os
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from keyboards import operator_control_keyboard, research_or_connect_keyboard
from glpi_search import perform_search

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPERATOR_CHAT_ID = os.getenv('OPERATOR_CHAT_ID')
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME')

client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
fsm_collection = db['fsm']  # Adjusted to specifically reference the 'fsm' collection
users_collection = db['users']  # Added explicit reference to the 'users' collection

class DialogStates(StatesGroup):
    waiting_for_search_query = State()
    waiting_for_user_input = State()
    in_conversation = State()

async def send_welcome(message: types.Message):
    await DialogStates.waiting_for_search_query.set()
    await message.answer("Здравствуйте! Пришлите мне ключевые слова для поиска в базе данных FAQ.", reply_markup=research_or_connect_keyboard())

async def handle_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Check if this is a reply in the operator's chat
    if message.reply_to_message and message.chat.id == int(OPERATOR_CHAT_ID):
        # Attempt to fetch the original user ID for whom the operator is replying
        original_user_id = await fetch_original_user_id(message.reply_to_message.message_id)
        if original_user_id:
            # Send the operator's reply back to the original user
            await message.bot.send_message(original_user_id, f"Ответ оператора: {message.text}")
            # Optionally, reset or update the state if needed
            await state.finish()  # or use `await state.set_state(SomeOtherState)`
            return
        else:
            logger.error("Original user ID not found for the reply.")
            return

    # Handle a user's search query when waiting for a search input
    if current_state == DialogStates.waiting_for_search_query.state:
        search_response, keyboard = await perform_search(message.text)
        await message.answer(search_response, reply_markup=keyboard)
        return

    # Handling forwarding of user messages to the operator
    if current_state == DialogStates.waiting_for_user_input.state:
        forwarded_msg = await message.bot.send_message(
            OPERATOR_CHAT_ID,
            f"Сообщение от {message.from_user.full_name} (@{message.from_user.username}): {message.text}",
            reply_markup=operator_control_keyboard()
        )
        # Link the forwarded message ID with the user's ID for tracking replies
        await db.message_links.insert_one({
            "reply_message_id": forwarded_msg.message_id,
            "original_user_id": message.from_user.id
        })
        await state.update_data(user_id=message.from_user.id, forwarded_message_id=forwarded_msg.message_id)
        await message.answer("Ваше сообщение отправлено оператору.")
        return

    # Default response if none of the above conditions are met
    #await message.answer("Please use the buttons to interact or start a new query with /start.")




async def fetch_original_user_id(reply_message_id):
    record = await db.message_links.find_one({"reply_message_id": reply_message_id})
    if record:
        return record['original_user_id']
    logger.error(f"No record found linking reply_message_id {reply_message_id} to an original user.")
    return None


async def handle_search_again(query: types.CallbackQuery, state: FSMContext):
    await DialogStates.waiting_for_search_query.set()
    await query.message.answer("Введите ключевые слова для нового поиска.")
    await query.answer()

async def handle_transfer_to_operator(query: types.CallbackQuery, state: FSMContext):
    await DialogStates.waiting_for_user_input.set()
    await query.message.answer("Пожалуйста, напишите ваше сообщение для оператора:")

async def end_conversation_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    await clear_conversation_state(user_id)
    await query.message.answer("Разговор завершен.")
    await query.bot.send_message(user_id, "Этот разговор был завершен оператором.")
    await state.finish()
    await query.answer()

async def block_user_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    await block_user_in_db(user_id)
    await query.message.answer("Пользователь был заблокирован.")
    await query.answer()

async def unblock_user_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    await unblock_user_in_db(user_id)
    await query.message.answer("Пользователь был разблокирован.")
    await query.answer()

async def block_user_in_db(user_id):
    await users_collection.update_one({'_id': user_id}, {'$set': {'blocked': True}})

async def unblock_user_in_db(user_id):
    await users_collection.update_one({'_id': user_id}, {'$set': {'blocked': False}})

async def clear_conversation_state(user_id):
    await users_collection.update_one({'_id': user_id}, {'$unset': {'conversation_state': ""}})

async def handle_help(message: types.Message):
    help_text = "Вот как вы можете взаимодействовать со мной:\n"
    help_text += "- Используйте кнопку поиска, чтобы начать новый поиск.\n"
    help_text += "- Выберите 'Связаться с оператором', чтобы отправить сообщение в нашу службу поддержки.\n"
    help_text += "- Отвечайте на любые подсказки, которые я предоставляю для детального взаимодействия."
    await message.answer(help_text)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'], state="*")
    dp.register_message_handler(handle_help, commands=['help'], state="*")
    dp.register_message_handler(handle_message, state="*")
    dp.register_callback_query_handler(handle_search_again, text='search_again', state="*")
    dp.register_callback_query_handler(handle_transfer_to_operator, text='transfer_to_operator', state="*")
    dp.register_callback_query_handler(end_conversation_handler, text='end_conversation', state=DialogStates.in_conversation)
    dp.register_callback_query_handler(block_user_handler, text='block_user', state=DialogStates.in_conversation)
    dp.register_callback_query_handler(unblock_user_handler, text='unblock_user', state=DialogStates.in_conversation)

if __name__ == "__main__":
    # Assuming 'dp' is your Dispatcher instance and you have a 'bot' instance
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
