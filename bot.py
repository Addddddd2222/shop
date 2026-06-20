import asyncio
import json
import aiohttp
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    BufferedInputFile
)

# ==========================================
# ТВОИ ДАННЫЕ
# ==========================================
TOKEN = "8839915917:AAHRdJ6WYs4En3PQ5Fdr2cxjTFDBgyxIzZM"
ADMIN_ID = 6067124228
WEB_APP_URL = "https://addddddd2222.github.io/shop/"
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
# ==========================================

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ==========================================
# ЗАГРУЗКА ТОВАРОВ
# ==========================================
try:
    with open("products.json", "r", encoding="utf-8") as f:
        ALL_PRODUCTS = json.load(f)
    print(f"✅ Загружено {len(ALL_PRODUCTS)} товаров с реальными брендами")
except:
    ALL_PRODUCTS = []
    print("❌ Не удалось загрузить products.json")

# ==========================================
# СОСТОЯНИЯ ДЛЯ ИИ
# ==========================================
class AIState(StatesGroup):
    waiting_for_question = State()

# ==========================================
# ГЛАВНОЕ МЕНЮ
# ==========================================
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Каталог")],
            [KeyboardButton(text="🔍 Поиск по ID"), KeyboardButton(text="🤖 Чат с ИИ")],
            [KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True
    )

def get_ai_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Выйти из ИИ")]],
        resize_keyboard=True
    )

# ==========================================
# СТАРТ
# ==========================================
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Добро пожаловать в Legit Drop!\n\n"
        "📦 Каталог — ссылка на сайт с товарами.\n"
        "🔍 Поиск по ID — найти товар по 5-значному ID.\n"
        "🤖 Чат с ИИ — задать вопрос.\n"
        "📞 Поддержка — связь с магазином.",
        reply_markup=get_main_keyboard()
    )

# ==========================================
# КНОПКА «КАТАЛОГ»
# ==========================================
@dp.message(F.text == "📦 Каталог")
async def catalog_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть каталог", web_app=types.WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(
        "Вот ссылка на наш каталог. Там ты найдёшь все товары и их ID:",
        reply_markup=kb
    )

# ==========================================
# КНОПКА «ПОДДЕРЖКА»
# ==========================================
@dp.message(F.text == "📞 Поддержка")
async def support_cmd(message: types.Message):
    await message.answer("Связь с поддержкой: @VVVVVV1199")

# ==========================================
# КНОПКА «ПОИСК ПО ID»
# ==========================================
@dp.message(F.text == "🔍 Поиск по ID")
async def find_by_id_start(message: types.Message):
    await message.answer(
        "Введите 5-значный ID товара (например, 10002, 10045 или 10072):",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отменить поиск")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "❌ Отменить поиск")
async def cancel_search(message: types.Message):
    await message.answer("Поиск отменён.", reply_markup=get_main_keyboard())

@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def find_by_id_result(message: types.Message):
    try:
        user_id = int(message.text)
        found = None
        for p in ALL_PRODUCTS:
            if p.get('id') == user_id:
                found = p
                break
        
        if not found:
            await message.answer("❌ Товар с таким ID не найден. Проверьте ID на сайте.")
            return
        
        name = found.get('name', 'Товар')
        brand = found.get('brand', 'Бренд')
        price = found.get('price_rub', 0)
        image_url = found.get('image', '')
        sizes = found.get('sizes', [])
        sizes_text = ", ".join(sizes[:5]) + ("..." if len(sizes) > 5 else "")
        
        caption = (
            f"<b>{brand}</b> {name}\n"
            f"💵 <b>{price}</b> ₽\n"
            f"📏 Размеры: {sizes_text}\n"
            f"🆔 ID: <b>#{user_id}</b>"
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        file_bytes = await resp.read()
                        input_file = BufferedInputFile(file_bytes, filename="photo.jpg")
                        await message.answer_photo(photo=input_file, caption=caption, parse_mode="HTML")
                        return
        except:
            pass
        
        await message.answer(caption, parse_mode="HTML")
        
    except:
        await message.answer("❌ Ошибка. Введите корректный ID.")

# ==========================================
# КНОПКА «ЧАТ С ИИ»
# ==========================================
@dp.message(F.text == "🤖 Чат с ИИ")
async def ai_cmd(message: types.Message, state: FSMContext):
    if not OPENROUTER_KEY:
        await message.answer("ИИ-помощник временно отключён.")
        return
    
    await message.answer(
        "🤖 ИИ-помощник активирован. Задайте ваш вопрос:",
        reply_markup=get_ai_keyboard()
    )
    await state.set_state(AIState.waiting_for_question)

@dp.message(AIState.waiting_for_question)
async def ai_ask(message: types.Message, state: FSMContext):
    if message.text == "❌ Выйти из ИИ":
        await state.clear()
        await message.answer("Вы вышли из режима ИИ.", reply_markup=get_main_keyboard())
        return
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": "Вы — вежливый помощник магазина Legit Drop. Отвечайте коротко, только по делу, на русском языке."},
            {"role": "user", "content": message.text}
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data['choices'][0]['message']['content']
                else:
                    answer = f"Ошибка ИИ (код {resp.status})."
    except:
        answer = "Ошибка соединения с ИИ. Попробуйте позже."
    
    await message.answer(answer)

# ==========================================
# ЗАПУСК БОТА
# ==========================================
async def main():
    print("✅ Бот Legit Drop с обновлёнными ID запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
