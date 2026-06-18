import asyncio
import json
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8839915917:AAHRdJ6WYs4En3PQ5Fdr2cxjTFDBgyxIzZM"
MY_TELEGRAM_ID = 6067124228
WEB_APP_URL = "https://addddddd2222.github.io/shop/"

# ===== КЛЮЧ OPENROUTER =====
import os
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class BotStates(StatesGroup):
    waiting_for_ai = State()

# ===== КЛАВИАТУРЫ =====
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👟 Открыть магазин Legit Drop", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="🤖 Чат с ИИ (Тест)", callback_data="start_ai_chat")],
        [InlineKeyboardButton(text="🚚 Условия доставки", callback_data="delivery")]
    ])

def get_exit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Выйти из чата с ИИ", callback_data="exit_ai_chat")]
    ])

# ===== ОБРАБОТЧИКИ =====
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "***Добро пожаловать в Legit Drop!*** ✨\n\n"
        "Мы возим оригинальную обувь напрямую с платформы Poizon (Dewu) по всей России. Никаких реплик - только 100% оригинальный стритвир со всеми фирменными пломбами.\n\n"
        "Нажмите на кнопки ниже, чтобы открыть приложение магазина или протестировать наш ИИ! 👇",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "delivery")
async def show_delivery(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "***🚚 Логистика Legit Drop:***\n\n"
        "1. **Выкуп:** Выкупаем ваш размер на Poizon in China.\n"
        "2. **Проверка:** Товар проходит контроль на оригинальность, получает бирюзовые пломбы.\n"
        "3. **Склад в РФ:** Посылка едет на наш склад в Уссурийске, где мы проверяем качество.\n"
        "4. **Отправка:** Отправляем посылку в ваш город через СДЭК или Почту.\n\n"
        "*Трек-номер выдаём сразу после отправки из Уссурийска!*"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "start_ai_chat")
async def start_ai_mode(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "🤖 **Режим ИИ-Помощника включен!**\n\n"
        "Теперь мы общаемся в режиме реального диалога. Ты можешь писать мне сколько угодно сообщений подряд.\n\n"
        "Чтобы закончить разговор и вернуться в меню, нажми кнопку ниже или напиши слово *выход*.",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(BotStates.waiting_for_ai)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "exit_ai_chat")
async def exit_ai_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("Вы вернулись в главное меню:", reply_markup=get_main_keyboard())
    await callback_query.answer()

# ===== ОБРАБОТЧИК ЗАКАЗОВ ИЗ МАГАЗИНА (С ДОБАВЛЕННЫМ УВЕДОМЛЕНИЕМ В ЧАТ) =====
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        items_text = ""
        total = data.get('total', 0)
        delivery = data.get('delivery', {})
        items = data.get('items', [])

        for idx, item in enumerate(items, start=1):
            items_text += (
                f"{idx}. {item.get('brand', '')} {item.get('name', '')}\n"
                f"   Размер: {item.get('size', '')}, Цвет: {item.get('color', '')}\n"
                f"   Кол-во: {item.get('quantity', 1)}, Цена: {item.get('price', 0)} ₽\n"
            )

        admin_message = (
            f"🛒 НОВЫЙ ЗАКАЗ!\n\n"
            f"📦 Состав заказа:\n{items_text}\n"
            f"💰 Общая сумма: {total} ₽\n\n"
            f"👤 Данные покупателя:\n"
            f"ФИО: {delivery.get('name', 'Не указано')}\n"
            f"Телефон: {delivery.get('phone', 'Не указан')}\n"
            f"Город: {delivery.get('city', 'Не указан')}\n"
            f"ПВЗ СДЭК: {delivery.get('pvz', 'Не указан')}\n"
        )

        # ==========================================
        # ОТПРАВКА ТЕБЕ В ЛИЧКУ (ID)
        # ==========================================
        await bot.send_message(chat_id=MY_TELEGRAM_ID, text=admin_message, parse_mode="Markdown")
        
        # ==========================================
        # ОТПРАВКА В ЧАТ С БОТОМ (САМОМУ ПОКУПАТЕЛЮ) - ДОБАВЛЕНО
        # ==========================================
        user_message = (
            f"✅ **Ваш заказ принят!**\n\n"
            f"📦 Состав заказа:\n{items_text}\n"
            f"💰 Общая сумма: {total} ₽\n\n"
            f"📍 Город доставки: {delivery.get('city', 'Не указан')}\n"
            f"📦 ПВЗ: {delivery.get('pvz', 'Не указан')}"
        )
        await message.answer(user_message, parse_mode="Markdown")

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("⚠️ Ошибка при оформлении заказа. Попробуйте ещё раз.")

# ===== ОБРАБОТЧИК ИИ-ЧАТА С OPENROUTER =====
@dp.message(BotStates.waiting_for_ai)
async def handle_ai_request(message: types.Message, state: FSMContext):
    text_check = message.text.lower().strip()
    if text_check in ["выход", "stop", "стоп", "exit"] or message.text.startswith("/"):
        await state.clear()
        await message.answer("Вы вернулись в главное меню:", reply_markup=get_main_keyboard())
        return

    if not OPENROUTER_KEY or OPENROUTER_KEY == "ВАШ_КЛЮЧ_СЮДА":
        await message.answer("⚠️ ИИ-помощник недоступен: ключ не настроен.")
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
                "content": "Ты — живой, вежливый ассистент стритвир-магазина Legit Drop. Общайся ВЕЖЛЕВО, как человек. Помогай подобрать кроссовки и шмот. Не используй дурацкий сленг. Отвечай коротко и только на русском языке."
            },
            {"role": "user", "content": message.text}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data['choices'][0]['message']['content']
                else:
                    answer = f"⚠️ Ошибка сервера ИИ (Код: {response.status})."
    except Exception as e:
        answer = f"⚠️ Не удалось связаться с ИИ. Ошибка: {str(e)}"

    await message.answer(answer, reply_markup=get_exit_keyboard())

# ===== ВСЕ ОСТАЛЬНЫЕ СООБЩЕНИЯ =====
@dp.message()
async def ignore_regular_text(message: types.Message):
    if message.text.startswith("/"):
        return
    await message.answer("Пожалуйста, используйте кнопки меню для взаимодействия с ботом.", reply_markup=get_main_keyboard())

async def main():
    print("Магазин Legit Drop успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
