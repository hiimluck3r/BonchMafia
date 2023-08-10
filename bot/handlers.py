import sys
import psycopg2
import random
import aiogram.utils.markdown as fmt
from PIL import Image, ImageFont, ImageDraw

from bot.disaptcher import dp, bot
from aiogram import types
from time import sleep
#from bot.controllers import //todo functions here
from bot import DB, USER, PASSWORD, HOST, ADMIN
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

"""
Подключение к БД
"""

while flag:
    try:
        conn = psycopg2.connect(dbname=DB, user=USER, password=PASSWORD, host=HOST) #указывать в .env
        print('Connection to database is established')
        flag = False
    except Exception as e:
        print("Can't establish connection to database. Error:", e)
        sleep(3)


"""
todo Блок для работы с блокировкой и разблокировкой пользователей
"""


"""
Главное меню
"""

@dp.message_handler(Text(equals="Техническая поддержка"))
async def support(message: types.Message):
    await message.answer(f'По всем вопросам обращайтесь в личные сообщения группы ВК (https://vk.com/bonchmafia).\nИли в наш телеграм канал (*ВСТАВИТЬ ССЫЛКУ ЗДЕСЬ*).')

@dp.message_handler(commands="start")
@dp.message_handler(Text(equals="Начать"))
async def greeter(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    goto_menu = types.KeyboardButton(text="Главное меню")
    keyboard.add(goto_menu)
    await message.answer(greet, reply_markup=keyboard)

"""
Блок с пользовательской картой
"""

@dp.message_handler(Text(equals="Моя карта"))
async def mycard(message: types.Message):
    userid = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE userid={userid}")
    userstats = cursor.fetchone()
    cursor.close()
    if len(userstats == 0):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Создать новую карту", callback_data="card_new.start"))
        await message.answer("Похоже, что вашей карты нет.", reply_markup=keyboard)
    else:
        userid = userstats[1]
        don = userstats[2]
        mafia = userstats[3]
        sheriff = userstats[4]
        citizen = userstats[5]
        won = userstats[6]
        lost = userstats[7]
        total = won+lost
        mentor = userstats[8]
        nickname = userstats[9]

        winrate = round(won/total)*100
        if total < 10:
            league = "calibration"
            winrate = 0
        
        if 10 <= total <= 48:
            winrate = round(won/48)*100
        else:
            winrate = round(won/total)*100

        if winrate <= 16:
            league = "bronze"
        elif 17 <= winrate <= 26:
            league = "silver"
        elif 27 <= winrate <= 37:
            league = "gold"
        elif 38 <= winrate <= 48:
            league = "platinum"
        elif 49 <= winrate <= 59:
            league = "ruby"
        elif winrate >= 60:
            league = "diamond"
        
        card = Image.open(f"frames/{league}_frame.png")
        font = ImageFont.truetype("Helvetica", 15)

        draw = ImageDraw.Draw(card)

        #draw.text() todo: make a proper text positioning and frames
        card.save(f"cards/{nickname}.png")
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Изменить изображение профиля", "Изменить никнейм"]
        keyboard.add(*buttons)
        keyboard.add(["Главное меню"])
        await message.answer_photo(f"cards/{nickname}.png", reply_markup=keyboard)

class CardSetup(StatesGroup):
    nickname = State()
    profile_picture = State()

@dp.callback_query_handler(Text(startswith="card_"))
async def card_manager(call: types.CallbackQuery):
    operation = call.data.split('_')[1]
    print(f'Found an operation: {operation}', file=sys.stderr)
    if operation == 'new.start':
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(["Отмена"])

            await CardSetup.nickname.set()
            await bot.send_message(chat_id = call.from_user.id,
            text = f"Введите свой никнейм:",
            reply_markup=keyboard)
        except Exception as e:
            print(f'Found an exception in card_manager.new.start option: {e}', file=sys.stderr)
    else:
        print(f'Found unresolved operation in card_manager: {operation}', file=sys.stderr)
    await call.answer()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Главное меню'])

    current_state = await state.get_state()
    if current_state is None:
        return

    print(f'Cancelling state %r', current_state, file=sys.stderr)
    await state.finish()

    await message.answer('Ввод данных остановлен.', reply_markup=keyboard)

@dp.message_handler(lambda message: any([len(message.text>20), len(message.text)<1, (if '.' in message.text), (if '/' in message.text), (if '_' in message.text)]), state=CardSetup.nickname)
async def process_nickname_invalid(message: types.Message):
    await CardSetup.nickname.set()
    return await message.answer(f'Неверный никнейм.\nИмя игрока не должно содержать символы "., /, _". Длина ника - от 1 до 20 символов.')

"""
Создание новой карты
"""

@dp.message_handler(state=CardSetup.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    try:
        async with state.proxy as data:
            data['nickname'] == message.text
    except Exception as e:
        print(f'Found an exception at process_nickname data parse: {e}', file=sys.stderr)

    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE (nickname = '{data['nickname']}');"
    cursor.execute(sql)
    overlapping_users = cursor.fetchall()
    cursor.close()
    if len(overlapping_users) >= 1:
        await CardSetup.nickname.set()

        await message.answer(f"Уже имеется пользователь с таким именем. Введите другой никнейм:")
    else:
        await AskQuestion.next()
        await message.answer(f"Теперь добавьте изображение профиля:")

@dp.message_handler(content_types=['any'], state=CardSetup.profile_picture)
async def process_profile_picture(message: types.Message):
    if message.photo:
        try:
            await message.photo[-1].download(f"profile/{data['nickname']}.png")
            
            cursor = conn.cursor()
            sql = f"INSERT INTO users(userid, don, mafia, sheriff, citizen, won, lost, mentor, nickname) VALUES ({message.from_user.id}, 0, 0, 0, 0, 0, 0, '-', '{data['nickname']}');"
            cursor.execute(sql)
            conn.commit()
            cursor.close()

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(["Главное меню"])
            await message.answer(f"Ваша карта была успешно добавлена. Приятных игр!")
        except Exception as e:
            print(f"Found an exception in process_profile_picture: {e}", file=sys.stderr)
    else:
        await CardSetup.profile_picture.set()
        
        await message.answer(f"Отправьте изображение (не как файл):")