import asyncio
import logging
import re
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)

# --- ДАННЫЕ --- ВВЕДИТЕ ЛИЧНЫЕ
TOKEN = "" 
ADMIN_IDS = []

CHANNELS = {
#    ADD YOUR CHANELS
}

# Магия: берем все ID из словаря CHANNELS автоматически
ALL_CHANNELS = list(CHANNELS.values())
CHATS_PER_PAGE = 8  # По сколько чатов показывать на одной странице

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class Broadcast(StatesGroup):
    waiting_for_all_text = State()
    waiting_for_single_text = State()

# --- ФУНКЦИЯ ГЕНЕРАЦИИ КНОПОК С ЛИСТАНИЕМ ---
def get_pagination_keyboard(page: int = 0):
    items = list(CHANNELS.items())
    start = page * CHATS_PER_PAGE
    end = start + CHATS_PER_PAGE
    current_items = items[start:end]

    builder = []
    for name, chat_id in current_items:
        builder.append([InlineKeyboardButton(text=name, callback_data=f"ch_{chat_id}")])

    # Кнопки навигации
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    if end < len(items):
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{page+1}"))
    
    if nav_row:
        builder.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=builder)

# --- ФУНКЦИЯ АВТО-ОБНОВЛЕНИЯ ФАЙЛА ---
def update_source_code(chat_name, chat_id):
    file_path = sys.argv[0]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if str(chat_id) not in content:
            # Добавляем в словарь CHANNELS
            new_entry = f'    "{chat_name}": {chat_id},'
            content = re.sub(r'(CHANNELS = \{)', r'\1\n' + new_entry, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        logging.error(f"Ошибка при записи: {e}")
    return False

# --- ОБРАБОТЧИКИ ---

@dp.my_chat_member()
async def on_my_chat_member_update(event: types.ChatMemberUpdated):
    if event.new_chat_member.status == "administrator":
        chat_name, chat_id = event.chat.title, event.chat.id
        if update_source_code(chat_name, chat_id):
            for admin_id in ADMIN_IDS:
                try: await bot.send_message(admin_id, f"✅ Чат <b>{chat_name}</b> добавлен! Перезапусти бота.")
                except: pass

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📢 все чаты"), KeyboardButton(text="🎯 отдельный чат")]], 
    resize_keyboard=True
)

confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить и отправить", callback_data="finish_send")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_send")]
])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    await message.answer("<b>Панель управления рассылкой:</b>", reply_markup=main_kb)

@dp.message(F.text == "📢 все чаты")
async def start_all_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.set_state(Broadcast.waiting_for_all_text)
    await message.answer("Пришли текст для рассылки во все чаты:")

@dp.message(Broadcast.waiting_for_all_text)
async def get_all_text(message: types.Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text, target="all")
    await message.answer(f"<b>Превью:</b>\n\n{message.text}", reply_markup=confirm_kb)

@dp.message(F.text == "🎯 отдельный чат")
async def show_channels(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    await message.answer("Выберите чат из списка:", reply_markup=get_pagination_keyboard(0))

@dp.callback_query(F.data.startswith("page_"))
async def process_pagination(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(reply_markup=get_pagination_keyboard(page))
    await callback.answer()

@dp.callback_query(F.data.startswith("ch_"))
async def select_channel(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_chat=callback.data.split("_")[1])
    await state.set_state(Broadcast.waiting_for_single_text)
    await callback.message.edit_text("Введите текст для этого чата:")

@dp.message(Broadcast.waiting_for_single_text)
async def get_single_text(message: types.Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text, target="single")
    await message.answer(f"<b>Превью:</b>\n\n{message.text}", reply_markup=confirm_kb)

@dp.callback_query(F.data == "cancel_send")
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отменено.")

@dp.callback_query(F.data == "finish_send")
async def finish_broadcast(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text, target = data.get("broadcast_text"), data.get("target")

    if target == "all":
        count = 0
        for ch_id in ALL_CHANNELS:
            try:
                await bot.send_message(ch_id, text)
                count += 1
            except: pass
        await callback.message.edit_text(f"✅ Отправлено в {count} чатов!")
    else:
        try:
            await bot.send_message(data.get("target_chat"), text)
            await callback.message.edit_text("✅ Отправлено!")
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    print(f"Бот запущен. Админов: {len(ADMIN_IDS)}. Каналов в списке: {len(ALL_CHANNELS)}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("Бот выключен")