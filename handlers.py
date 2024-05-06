import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from keyboards import research_or_connect_keyboard, operator_keyboard
from glpi_search import perform_search
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPERATOR_CHAT_ID = os.getenv('OPERATOR_CHAT_ID')  # ID чата операторов

class DialogStates(StatesGroup):
    waiting_for_search_query = State()
    waiting_for_user_message = State()
    waiting_for_operator_response = State()

async def send_welcome(message: types.Message):
    await DialogStates.waiting_for_search_query.set()
    await message.answer("Привет! Отправь мне ключевые слова для поиска в базе знаний FAQ.")

async def handle_message(message: types.Message, state: FSMContext):
    if await state.get_state() == DialogStates.waiting_for_search_query.state:
        response_message, keyboard = await perform_search(message.text)
        await message.answer(response_message, reply_markup=keyboard)
        await state.finish()

async def handle_search_again(query: types.CallbackQuery):
    await DialogStates.waiting_for_search_query.set()
    await query.message.answer("Введите ключевые слова для нового поиска.")
    await query.answer()

async def handle_transfer_to_operator(query: types.CallbackQuery):
    await DialogStates.waiting_for_user_message.set()
    await query.message.answer("Какое сообщение переслать оператору?")
    await query.answer()

async def handle_user_message_for_operator(message: types.Message, state: FSMContext):
    if await state.get_state() == DialogStates.waiting_for_user_message.state:
        user_info = f"От {message.from_user.full_name} (@{message.from_user.username}): {message.text}"
        sent_message = await message.bot.send_message(OPERATOR_CHAT_ID, user_info, reply_markup=operator_keyboard())
        await state.update_data(original_message_id=sent_message.message_id, user_id=message.from_user.id)
        logger.debug(f"Сохраненные данные: original_message_id={sent_message.message_id}, user_id={message.from_user.id}")
        await message.answer("Сообщение отправлено оператору.")
        await DialogStates.waiting_for_operator_response.set()

async def handle_operator_reply(message: types.Message, state: FSMContext):
    if await state.get_state() == DialogStates.waiting_for_operator_response.state and message.reply_to_message:
        data = await state.get_data()
        logger.debug(f"Полученные данные: {data}")
        if 'original_message_id' in data and message.reply_to_message.message_id == data['original_message_id']:
            user_id = data['user_id']
            await message.bot.send_message(user_id, f"Ответ от оператора: {message.text}")
            await state.finish()
        else:
            logger.error("Не удалось связать ответ оператора с запросом пользователя.")
            await message.answer("Не удалось связать этот ответ с запросом пользователя.")

async def handle_answer_callback(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'answer':
        await query.message.reply("Введите ответ для пользователя.")
        await state.set_state(DialogStates.waiting_for_operator_response)
        await query.answer()

def register_handlers(dp):
    dp.register_message_handler(send_welcome, commands=["start"], state="*")
    dp.register_message_handler(handle_message, state=DialogStates.waiting_for_search_query)
    dp.register_message_handler(handle_user_message_for_operator, state=DialogStates.waiting_for_user_message)
    dp.register_message_handler(handle_operator_reply, state=DialogStates.waiting_for_operator_response, is_reply=True)
    dp.register_callback_query_handler(handle_search_again, text="search_again")
    dp.register_callback_query_handler(handle_transfer_to_operator, text="transfer_to_operator")
    dp.register_callback_query_handler(handle_answer_callback, text="answer")
