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
    InputMediaPhoto, BufferedInputFile
)

# ==========================================
# ТВОИ ДАННЫЕ (ВСТАВЬ СЮДА)
# ==========================================
TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER"
ADMIN_ID = 6067124228  # Твой личный ID
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")  # Если есть ключ ИИ
# ==========================================

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ==========================================
# ЗАГРУЗКА ТОВАРОВ ИЗ JSON
# ==========================================
try:
    with open("products.json", "r", encoding="utf-8") as f:
        ALL_PRODUCTS = json.load(f)
    print(f"✅ Загружено {len(ALL_PRODUCTS)} товаров")
except:
    ALL_PRODUCTS = []
    print("❌ Не удалось загрузить products.json")

# ==========================================
# СОСТОЯНИЯ ДЛЯ ЗАКАЗА И ИИ
# ==========================================
class OrderState(StatesGroup):
    waiting_for_size = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_city = State()
    waiting_for_pvz = State()

class AIState(StatesGroup):
    waiting_for_question = State()

# ==========================================
# КНОПКИ ГЛАВНОГО МЕНЮ
# ==========================================
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Каталог")],
            [KeyboardButton(text="🤖 ИИ-помощник"), KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True
    )

# ==========================================
# КНОПКИ КАТЕГОРИЙ
# ==========================================
def get_category_keyboard():
    categories = {}
    for p in ALL_PRODUCTS:
        cat = p.get('category', 'Разное')
        if cat not in categories:
            categories[cat] = []
    
    kb = []
    row = []
    for cat in categories.keys():
        row.append(InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==========================================
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ БРЕНДОВ ПО КАТЕГОРИИ
# ==========================================
def get_brand_keyboard(category):
    brands = set()
    for p in ALL_PRODUCTS:
        if p.get('category') == category:
            brands.add(p.get('brand', 'Бренд'))
    
    kb = []
    row = []
    for brand in brands:
        row.append(InlineKeyboardButton(text=brand, callback_data=f"brand_{category}_{brand}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="back_to_cats")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==========================================
# КНОПКИ ДЛЯ КАРТОЧКИ ТОВАРА (ПАГИНАЦИЯ И ЗАКАЗ)
# ==========================================
def get_product_keyboard(index, total, category, brand, product_id):
    nav = []
    if index > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"nav_{category}_{brand}_{index-1}"))
    if index < total - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"nav_{category}_{brand}_{index+1}"))
    
    kb = []
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_{product_id}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад к брендам", callback_data=f"back_to_brand_{category}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==========================================
# ОБРАБОТЧИК КОМАНДЫ /start
# ==========================================
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"Добро пожаловать в магазин **Legit Drop**!\n\n"
        f"Здесь вы можете найти оригинальный стритвир.\n"
        f"Используйте кнопки ниже для навигации:",
        reply_markup=get_main_keyboard()
    )

# ==========================================
# ОБРАБОТЧИК КНОПОК МЕНЮ
# ==========================================
@dp.message(F.text == "📦 Каталог")
async def catalog_cmd(message: types.Message):
    await message.answer(
        "Выберите категорию товаров:",
        reply_markup=get_category_keyboard()
    )

@dp.message(F.text == "📞 Поддержка")
async def support_cmd(message: types.Message):
    await message.answer(
        "Для связи с поддержкой напишите сюда:\n"
        "👉 @VVVVVV1199"
    )

@dp.message(F.text == "🤖 ИИ-помощник")
async def ai_cmd(message: types.Message, state: FSMContext):
    if not OPENROUTER_KEY:
        await message.answer("ИИ-помощник временно отключён.")
        return
    
    await message.answer(
        "🤖 ИИ-помощник активирован. Задайте ваш вопрос:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Выйти из ИИ")]],
            resize_keyboard=True
        )
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
            {
                "role": "system",
                "content": "Вы — вежливый помощник магазина Legit Drop. Отвечайте коротко, только по делу, на русском языке."
            },
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
# ОБРАБОТЧИКИ INLINE КНОПОК (КАТАЛОГ, БРЕНДЫ, ТОВАРЫ)
# ==========================================
@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery):
    category = callback.data.replace("cat_", "")
    await callback.message.edit_text(
        f"Категория: **{category}**\n\nВыберите бренд:",
        reply_markup=get_brand_keyboard(category)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("brand_"))
async def process_brand(callback: types.CallbackQuery):
    _, category, brand = callback.data.split("_", 2)
    products = [p for p in ALL_PRODUCTS if p.get('category') == category and p.get('brand') == brand]
    if not products:
        await callback.answer("Нет товаров в этом бренде.")
        return
    
    p = products[0]
    await show_product_card(callback.message, p, category, brand, 0, products)
    await callback.answer()

async def show_product_card(message, product, category, brand, index, products):
    name = product.get('name', 'Товар')
    price = product.get('price_rub', 0)
    image_url = product.get('image', '')
    sizes = product.get('sizes', [])
    sizes_text = ", ".join(sizes[:5]) + ("..." if len(sizes) > 5 else "")
    
    caption = (
        f"<b>{brand}</b> {name}\n"
        f"💵 <b>{price}</b> ₽\n"
        f"📏 Размеры: {sizes_text}"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    file_bytes = await resp.read()
                    input_file = BufferedInputFile(file_bytes, filename="photo.jpg")
                    await message.edit_media(
                        media=InputMediaPhoto(media=input_file, caption=caption, parse_mode="HTML"),
                        reply_markup=get_product_keyboard(index, len(products), category, brand, product.get('id', index))
                    )
                    return
    except:
        pass
    
    await message.edit_text(
        text=caption + "\n\n⚠️ Фото не загрузилось.",
        parse_mode="HTML",
        reply_markup=get_product_keyboard(index, len(products), category, brand, product.get('id', index))
    )

@dp.callback_query(lambda c: c.data.startswith("nav_"))
async def process_nav(callback: types.CallbackQuery):
    _, category, brand, index = callback.data.split("_", 3)
    index = int(index)
    products = [p for p in ALL_PRODUCTS if p.get('category') == category and p.get('brand') == brand]
    p = products[index]
    await show_product_card(callback.message, p, category, brand, index, products)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("back_to_brand_"))
async def back_to_brand(callback: types.CallbackQuery):
    category = callback.data.replace("back_to_brand_", "")
    await callback.message.edit_text(
        f"Категория: **{category}**\n\nВыберите бренд:",
        reply_markup=get_brand_keyboard(category)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_cats")
async def back_to_cats(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию товаров:",
        reply_markup=get_category_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Вы в главном меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# ==========================================
# ОБРАБОТЧИК ЗАКАЗА
# ==========================================
@dp.callback_query(lambda c: c.data.startswith("order_"))
async def process_order(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.replace("order_", "")
    try:
        product = ALL_PRODUCTS[int(product_id)]
    except:
        product = ALL_PRODUCTS[0]
    
    await state.update_data(product=product)
    await callback.message.answer(
        f"Оформление заказа\n\n"
        f"Товар: {product.get('brand')} {product.get('name')}\n"
        f"Цена: {product.get('price_rub')} ₽\n\n"
        f"Введите нужный <b>размер</b>:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                ["36", "37", "38", "39", "40"],
                ["41", "42", "43", "44", "45"],
                ["S", "M", "L", "XL"],
                ["❌ Отменить"]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(OrderState.waiting_for_size)
    await callback.answer()

@dp.message(OrderState.waiting_for_size)
async def get_size(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    await state.update_data(size=message.text)
    await message.answer("Введите ваше <b>ФИО</b>:", parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите <b>номер телефона</b> (например, +7 999 123 45 67):", parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите <b>город</b> доставки:", parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_city)

@dp.message(OrderState.waiting_for_city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введите <b>адрес ПВЗ</b>:", parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_pvz)

@dp.message(OrderState.waiting_for_pvz)
async def get_pvz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product = data.get('product', {})
    
    admin_msg = (
        f"🛒 НОВЫЙ ЗАКАЗ!\n\n"
        f"Товар: {product.get('brand')} {product.get('name')}\n"
        f"Цена: {product.get('price_rub')} ₽\n"
        f"Размер: {data.get('size', 'Не указан')}\n"
        f"ФИО: {data.get('name', 'Не указано')}\n"
        f"Телефон: {data.get('phone', 'Не указан')}\n"
        f"Город: {data.get('city', 'Не указан')}\n"
        f"ПВЗ: {message.text}\n"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        await message.answer(
            "✅ Заказ принят!\n\n"
            "Скоро с вами свяжется менеджер.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    except:
        await message.answer("Ошибка при оформлении заказа. Попробуйте позже.")
        await state.clear()

# ==========================================
# ЗАПУСК БОТА
# ==========================================
async def main():
    print("✅ Бот Legit Drop запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
