import logging
from google.oauth2 import service_account
from aiogram.types import Message
from dotenv import load_dotenv
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import WebAppInfo
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import json
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot("токен бота")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('words.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id SERIAL,
        word TEXT,
        translation TEXT,
        status TEXT DEFAULT 'learning' 
    )
""")

SENTENCES_FILE = "web/Mods/translate.json"

if not os.path.exists("web/Mods"):
    os.makedirs("web/Mods")

if not os.path.exists(SENTENCES_FILE):
    with open(SENTENCES_FILE, "w", encoding="utf-8") as f:
        json.dump({"sentences": []}, f, ensure_ascii=False, indent=4)


class UploadFile(StatesGroup):
    waiting_for_file = State()


class UploadWords(StatesGroup):
    waiting_for_words = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Флеш Карточки", web_app=WebAppInfo(
        url="https://")))
    markup.add(types.KeyboardButton("Слово-Перевод", web_app=WebAppInfo(
        url="https://")))
    markup.add(types.KeyboardButton("Перевод предложений", web_app=WebAppInfo(
        url="https://")))
    markup.add(types.KeyboardButton("Профиль", web_app=WebAppInfo(
        url="https://")))

    await message.answer(
        "Привет! Этот бот поможет тебе прокачать твой словарный запас.", reply_markup=markup)



@dp.message_handler(commands=["upload_sentences"])
async def upload_sentences_command(message: types.Message):
    await message.answer("Пожалуйста, отправьте файл с предложениями в формате .txt. \n"
                         "Каждая строка должна содержать предложение на русском и на английском, разделенные ':'")
    await UploadFile.waiting_for_file.set()


@dp.message_handler(commands=["upload_words"])
async def upload_words_command(message: types.Message):
    await message.answer("Пожалуйста, отправьте файл со словами в формате .txt. \n"
                         "Каждая строка должна содержать слово на русском и его перевод на английский, разделенные ':'")
    await UploadWords.waiting_for_words.set()



@dp.message_handler(content_types=['document'], state=UploadFile.waiting_for_file)
async def process_file(message: types.Message, state: FSMContext):
    try:
        if not message.document.file_name.endswith('.txt'):
            await message.answer("Неверный формат файла. Пожалуйста, отправьте файл в формате .txt.")
            return

        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        file_content = downloaded_file.getvalue().decode('utf-8')
        lines = file_content.split('\n')

        with open(SENTENCES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sentences = data.get("sentences", [])

        for line in lines:
            line = line.strip()
            if line and ':' in line:
                russian, english = line.split(':', 1)
                sentences.append({"russian": russian.strip(), "english": english.strip()})

        with open(SENTENCES_FILE, "w", encoding="utf-8") as f:
            json.dump({"sentences": sentences}, f, ensure_ascii=False, indent=4)

        await message.answer("Файл успешно загружен и обработан!")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {e}")

    finally:
        await state.finish()


@dp.message_handler(content_types=['document'], state=UploadWords.waiting_for_words)
async def process_words_file(message: types.Message, state: FSMContext):
    try:
        if not message.document.file_name.endswith('.txt'):
            await message.answer("Неверный формат файла. Пожалуйста, отправьте файл в формате .txt.")
            return

        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        file_content = downloaded_file.getvalue().decode('utf-8')
        lines = file_content.split('\n')

        for line in lines:
            line = line.strip()
            if line and ':' in line:
                word, translation = line.split(':', 1)
                cursor.execute("INSERT INTO words (word, translation) VALUES (?, ?)",
                               (word.strip(), translation.strip()))

        conn.commit()
        await message.answer("Слова успешно добавлены в базу данных!")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {e}")

    finally:
        await state.finish()



async def on_startup(dp):
    await bot.set_my_commands([
        types.BotCommand("upload_sentences", "Загрузить предложения"),
        types.BotCommand("upload_words", "Загрузить слова"),
        types.BotCommand("start_chat_gemini", "Начать чат с AI-учителем"),
        types.BotCommand("stop_chat_gemini", "Завершить чат с AI-учителем"),
    ])




credentials = service_account.Credentials.from_service_account_file(
    "gen-lang-client-0525524462-3449a59add2b.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

GEMINI_API_KEY = os.getenv('апи')
genai.configure(api_key=GEMINI_API_KEY, credentials=credentials)

class ChatStates(StatesGroup):
    active_chat = State()
    idle = State()


@dp.message_handler(commands=["start_chat_gemini"])
async def start_chat(message: Message, state: FSMContext):
    await state.set_state(ChatStates.active_chat)
    await message.answer("Чат начат! Отправьте сообщение или нажмите 'Завершить чат с AI-учителем' чтобы завершить сессию.")

@dp.message_handler(commands=["stop_chat_gemini"])
async def start_chat(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Чат завершен.")
    return

@dp.message_handler(state=ChatStates.active_chat)
async def handle_message(message: Message):
    user_input = message.text
    try:
        waiting_message = await message.answer("⌛ Генерация ответа...")
        response = genai.chat(prompt=user_input)
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_message.message_id)
        await message.answer(response["candidates"][0]["content"])
    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации: {e}")

async def main():
    await dp.start_polling()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


