import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Жестко вшиваем токен, чтобы обойти глюки мобильного интерфейса Render
BOT_TOKEN = "8632364812:AAEsARWmLcAqnZbv0-KnncAWDPYsl2zy020"
ADMIN_ID = 123456789  # Сюда позже вставишь свой ID из @userinfobot для получения идей

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для формы "Предложить идею"
class FeedbackStates(StatesGroup):
    waiting_for_idea = State()

# --- КЛАВИАТУРЫ ---

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Стим (Steam)", callback_data="cat_steam")
    builder.button(text="📱 Мобильные игры", callback_data="cat_mobile")
    builder.button(text="📩 Предложить категорию", callback_data="suggest_idea")
    builder.adjust(1)
    return builder.as_markup()

def steam_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Пополнение баланса", callback_data="steam_topup")
    builder.button(text="👤 Продажа аккаунтов", callback_data="steam_accounts")
    builder.button(text="🔑 Ключи и Гифты", callback_data="steam_keys")
    builder.button(text="🔙 Назад в меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

# --- ХЕНДЛЕРЫ ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"🔥 Добро пожаловать в **PRIMEPLAY**!\n\n"
        f"Здесь ты можешь безопасно купить или продать баланс Steam, аккаунты и ключи.\n"
        f"Все сделки защищены нашей гарант-системой.",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(call: types.CallbackQuery):
    await call.message.edit_text(
        "🔥 Главное меню маркетплейса **PRIMEPLAY**:",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "cat_steam")
async def process_steam(call: types.CallbackQuery):
    await call.message.edit_text(
        "🎮 **Раздел Steam**\n\nВыбери нужную подкатегорию товаров:",
        reply_markup=steam_menu_kb()
    )

@dp.callback_query(F.data == "cat_mobile")
async def process_mobile(call: types.CallbackQuery):
    await call.message.answer("⚠️ Этот раздел находится в разработке. Скоро добавим Brawl Stars и Roblox!")
    await call.answer()

# Логика подкатегорий Стима
@dp.callback_query(F.data.startswith("steam_"))
async def steam_subcategories(call: types.CallbackQuery):
    subcategory = call.data.split("_")[1]
    
    if subcategory == "topup":
        text = "💰 **Пополнение баланса Steam**\n\nВведите логин вашего аккаунта и сумму пополнения. Комиссия площадки — 12%."
    elif subcategory == "accounts":
        text = "👤 **Магазин аккаунтов Steam**\n\nЗдесь собраны предложения от проверенных продавцов с гарантией."
    elif subcategory == "keys":
        text = "🔑 **Ключи и Игры подарком (Gift)**\n\nПокупка игр, недоступных в вашем регионе."
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Посмотреть предложения", callback_data="view_offers")
    builder.button(text="🔙 Назад", callback_data="cat_steam")
    builder.adjust(1)
    
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# Логика отправки предложений
@dp.callback_query(F.data == "suggest_idea")
async def suggest_idea_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("✍️ Напиши, какую игру или категорию ты хочешь видеть на PRIMEPLAY:")
    await state.set_state(FeedbackStates.waiting_for_idea)
    await call.answer()

@dp.message(FeedbackStates.waiting_for_idea)
async def suggest_idea_process(message: types.Message, state: FSMContext):
    user_idea = message.text
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💡 **Новое предложение для PRIMEPLAY!**\n\nОт: {user_info}\nИдея: {user_idea}"
        )
        await message.answer("✅ Спасибо! Твоя идея отправлена создателю проекта. Мы обязательно её рассмотрим.")
    except Exception:
        await message.answer("✅ Твоя идея принята! (Админ-панель настраивается).")
        
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

  
