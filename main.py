import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token="6354875653:AAEmq3GWfV7_86zmmPTArkHu1BJ4-KUoIkA")
dp = Dispatcher(bot, storage=MemoryStorage())
DB_NAME = 'mebel1_db.sqlite'

ADMIN_CHAT_ID = 329670694
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                fullname TEXT NOT NULL,
                phone TEXT NOT NULL
                )""")

TABLE_NAME = 'mebel1'
ID_COL = 'id'
PHOTO_COL = 'photo'
MEBEL_TYPE_COL = 'mebel_type'
DESCRIPTION_COL = 'description'
PRICE_COL = 'price'

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    {ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT,
    {PHOTO_COL} TEXT NOT NULL,
    {MEBEL_TYPE_COL} TEXT NOT NULL,
    {DESCRIPTION_COL} TEXT,
    {PRICE_COL} INTEGER NOT NULL
);
""")
SELECT_ALL_QUERY = """
SELECT * FROM mebel1;
"""


class Registr(StatesGroup):
    fullname = State()
    phone = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM user WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    if message.from_user.id == ADMIN_CHAT_ID:
        user = message.from_user.first_name
        print(f"{user} bo'tga kirdi", )
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('🪑 Mebellar'))
        keyboard.add(types.KeyboardButton('👨‍💼 Administrator'))
        await message.answer('Assalomu alaykum! Botimizga xush kelibsiz.', reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if user_data:
            user = message.from_user.first_name
            print(f"{user} botga kiridi")
            keyboard.add(types.KeyboardButton('🪑 Mebellar'))
            await message.answer(f"Assalomu alaykum! {user_data[1]} Botimizga xush kelibsiz.", reply_markup=keyboard)
        else:
            user = message.from_user.first_name
            print(f"yangi user{user}botga kiridi")
            await message.reply("Assalomu alaykum! ismingizni kiritind.")
            await state.set_state(Registr.fullname.state)


@dp.message_handler(lambda message: message.text == '🪑 Mebellar')
async def mebel_menu(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}mebelar buttoni bosildi")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(types.KeyboardButton('🍽 Kuxniy mebel'))
    keyboard.add(types.KeyboardButton('🛏 Spalniy mebel'))
    keyboard.add(types.KeyboardButton('🚪 Eshiklar'))
    keyboard.add(types.KeyboardButton('🧒 Detskiy mebel'))
    keyboard.add(types.KeyboardButton("orqaga"))
    await message.answer('Mebellar turini tanlang:', reply_markup=keyboard)


@dp.message_handler(text='orqaga')
async def orqaga(message: types.message):
    user = message.from_user.first_name
    print(f"{user}orqaga buttoni bosildi")
    await message.reply(f"/start tugmasini bosing orqaga qaytasiz")


@dp.message_handler(lambda message: message.text in ['🍽 Kuxniy mebel', '🛏 Spalniy mebel', '🚪 Eshiklar', '🧒 Detskiy mebel'])
async def show_mebel_by_type(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}mebelarni ko'rish bosildi")
    mebel_type = message.text[2:].lower()
    cursor.execute(f"SELECT * FROM mebel1 WHERE mebel_type='{mebel_type}'")
    mebels = cursor.fetchall()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    sotib = types.InlineKeyboardButton('sotib olish', callback_data='buy')
    keyboard_markup.add(sotib)
    if not mebels:
        await message.answer(f"{mebel_type.capitalize()} mebellari topilmadi.")
        return
    for mebel in mebels:
        id, photo, mebel_type, izohlar, narxi = mebel
        caption = f"{mebel_type.capitalize()}\n\n"
        if izohlar:
            caption += f"{izohlar}\n\n"
        caption += f"Narxi: {narxi} so'm"
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption, parse_mode=ParseMode.HTML,
                             reply_markup=keyboard_markup)


@dp.message_handler(text='👨‍💼 Administrator')
async def admin_menu(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}administrator buttoni bosildi")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('📤 Yangi mebel qo\'shish'))
    keyboard.add(types.KeyboardButton('📥 Mebellarni ko\'rish'))
    keyboard.add(types.KeyboardButton("orqaga"))
    await message.answer('Administrator menyusini tanlang:', reply_markup=keyboard)


class Add(StatesGroup):
    photo_id = State()
    mebel_type = State()
    price = State()
    comment = State()


@dp.message_handler(lambda message: message.text == '📤 Yangi mebel qo\'shish')
async def add_test(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}yangi mebel qoshish butoni bosildi")
    if message.from_user.id == ADMIN_CHAT_ID:
        await message.answer('Rasmni yuboring:')
        await Add.photo_id.set()
    else:
        await message.reply("siz admin emasiz")


@dp.message_handler(state=Add.photo_id, content_types=['photo'])
async def answer_photo_id(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user}rasm qoyvoti")
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Kuxniy mebel'))
    keyboard.add(types.KeyboardButton('Spalniy mebel'))
    keyboard.add(types.KeyboardButton('Eshiklar'))
    keyboard.add(types.KeyboardButton('Detskiy mebel'))
    await message.reply("mebelni typeni kiriting", reply_markup=keyboard)
    await Add.mebel_type.set()


@dp.message_handler(state=Add.mebel_type)
async def answer_mebel_type(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user}typeni tanlavodi")
    mebel_type = message.text.lower()
    await state.update_data(mebel_type=mebel_type)
    await message.answer('Mebel narxini kiriting:')
    await Add.price.set()


@dp.message_handler(state=Add.price)
async def price_answer(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user}narxini kiritvoti", )
    try:
        price = int(message.text)
        await state.update_data(price=price)
    except ValueError:
        await message.answer('Narx son ko\'rinishida emas!')
        return
    await message.answer('Izoh qoldiring:')
    await Add.comment.set()


@dp.message_handler(state=Add.comment)
async def cooment_answer(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user}izoh qoldirvoti")
    comment = message.text
    await state.update_data(comment=comment)
    async with state.proxy() as data:
        photo_id = data['photo_id']
        mebel_type = data['mebel_type']
        price = data['price']
        comment = data['comment']
        cursor.execute(
            f"INSERT INTO {TABLE_NAME}( {PHOTO_COL}, {MEBEL_TYPE_COL}, {DESCRIPTION_COL}, {PRICE_COL}) VALUES (?, ?, ?, ?)",
            (photo_id, mebel_type, comment, price))
        conn.commit()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('📤 Yangi mebel qo\'shish'))
        keyboard.add(types.KeyboardButton('📥 Mebellarni ko\'rish'))
        await message.answer('mebel muvaffaqiyatli qo\'shildi!', reply_markup=keyboard)
        user = message.from_user.first_name
        print(f"{user}yangi mebel qo'shdi")
        await state.finish()


@dp.callback_query_handler(text='buy')
async def buy_handler(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}mebel sotib olinvoti")
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    await bot.send_message(chat_id=ADMIN_CHAT_ID,text=f"Foydalanuvchi ma'lumotlari:\nID: {user_data[0]}\nIsm: {user_data[1]}\nnomeri: {user_data[2]}")
    await message.reply("adminga yuborildi")


@dp.message_handler(text='📥 Mebellarni ko\'rish')
async def show_all_mebels(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}admin mebelarni korvoti")
    if message.from_user.id != ADMIN_CHAT_ID:
        await message.answer('Siz administrator emassiz!')
        return
    cursor.execute(SELECT_ALL_QUERY)
    mebels = cursor.fetchall()
    if not mebels:
        await message.answer('Mebellar topilmadi!')
        return
    for mebel in mebels:
        id, photo, mebel_type, izohlar, narxi = mebel
        caption = f"{mebel_type.capitalize()}\n\n"
        if izohlar:
            caption += f"{izohlar}\n\n"
        caption += f"Narxi: {narxi} so'm"
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=["set_fullname"])
async def set_fullname(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user} ismini o'zgartirvoti")
    await message.reply("Yangi ismingiz va familiyangizni yuboring.")
    user_id = message.chat.id
    cursor.execute("SELECT fullname FROM user WHERE id=?", (user_id,))
    fullname = cursor.fetchone()[0]
    await message.reply(f"hozirgi ismi familiyangiz: {fullname} yangisini kiriting.")
    await state.set_state('set_fullname')


@dp.message_handler(state='set_fullname')
async def get_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    fullname_value = message.text
    cursor.execute(f"UPDATE users SET phone='{fullname_value}'where id=?", (user_id,))
    await message.reply(f"malumotlaringiz o'zgardi")
    await state.finish()


@dp.message_handler(commands=["set_number"])
async def set_number(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user}raqamani o'zgartirvoti")
    user_id = message.chat.id
    phone_number = cursor.execute("SELECT phone FROM user WHERE id=?", (user_id,))
    phone_number = phone_number.fetchone()[0]
    await message.reply(f"Hozirgi telefon raqamingiz: {phone_number}. Yangi telefon raqamingizni yuboring.")
    await state.set_state('phone_number')


@dp.message_handler(state='phone_number')
async def get_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    phone_value = message.text
    cursor.execute(f"UPDATE user SET phone='{phone_value}'where id=?", (user_id,))
    await message.reply(f"malumotlaringiz o'zgardi")
    await state.finish()


@dp.message_handler(commands=["info"])
async def get_user_info(message: types.Message):
    user = message.from_user.first_name
    print(f"{user}o'zi haqida malumot ko'rmoqchi", )
    user_id = message.chat.id
    cursor.execute("SELECT * FROM user WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        full_name = user_data[1]
        phone_number = user_data[2]
        info_text = f"Ismingiz va familiyangiz: {full_name}\nTelefon raqamingiz: {phone_number}"
        await message.reply(info_text)
    else:
        await message.reply("Siz ro'yxatdan o'tmaganmisiz. /start komandasini bosing.")


@dp.message_handler(commands=["royhatdan_o'tish"])
async def registration_form(message: types.Message, state: FSMContext):
    user = message.from_user.first_name
    print(f"{user} royhatdan o'tvoti",)
    keyboard = InlineKeyboardMarkup()
    cancel_button = InlineKeyboardButton(text="Bekor qilish", callback_data="cancel")
    keyboard.add(cancel_button)
    name = message.from_user.first_name
    print(name)
    await message.reply(f"ismingizni kiriting", reply_markup=keyboard)
    await state.set_state(Registr.fullname.state)


@dp.message_handler(state=Registr.fullname)
async def get_fullname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = message.from_user.first_name
        print(name)
        data["fullname"] = message.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('telefon raqamingiz', request_contact=True))
    await message.reply("Telefon raqamingizni yuboring.")
    await Registr.next()


@dp.message_handler(state=Registr.phone,)
async def get_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone"] = message.text
        user_id = message.chat.id
        full_name = data["fullname"]
        phone_number = data["phone"]
        cursor.execute("INSERT INTO user (id, fullname, phone) VALUES (?, ?, ?)",
                       (user_id, full_name, phone_number,))
    await message.reply("Ro'yxatdan o'tdingiz! /start komandasini bosing.")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cancel_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Ro'yxatdan o'tish bekor qilindi.")
    await state.finish()



if __name__ == "__main__":
    print("hurmatli Javohir tabrikliman botingiz xatosiz ishga tushdi")
    executor.start_polling(dp)
