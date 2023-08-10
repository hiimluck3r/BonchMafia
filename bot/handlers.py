import sys
import psycopg2
import random
import aiogram.utils.markdown as fmt
from PIL import Image, ImageFont, ImageDraw

from bot.dispatcher import dp, bot
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
flag = True
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

greet = "Добро пожаловать в клуб BonchMafia! Этот текст - плейсхолдер, его нужно заменить после разработки."

@dp.message_handler(commands="start")
async def greeter(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    goto_menu = types.KeyboardButton(text="Главное меню")
    keyboard.add(goto_menu)
    await message.answer(greet, reply_markup=keyboard)


@dp.message_handler(Text(equals="Главное меню"))
async def main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Моя карта", "Топ игроков"]
    keyboard.add(*buttons)
    buttons = ["Техническая поддержка"]
    keyboard.add(*buttons)
    await message.answer(f"Главное меню", reply_markup=keyboard)

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
    if userstats is None:
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

        if total < 10:
            league = "calibration"
            winrate = 0
        elif 10 <= total <= 48:
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
        
        card = Image.open(f"/~/BonchMafia/bot/pictures/frames/{league}_frame.png")
        #font = ImageFont.truetype("Helvetica", 15)

        #draw = ImageDraw.Draw(card) todo

        #draw.text() todo: make a proper text positioning and frames
        card.save(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png")
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Изменить изображение профиля", "Изменить никнейм"]
        keyboard.add(*buttons)
        buttons = ["Главное меню"]
        keyboard.add(*buttons)
        card_photo = open(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png", 'rb')
        await message.answer_photo(card_photo, reply_markup=keyboard,
        caption="Ваша карта")

class CardSetup(StatesGroup):
    nickname = State()
    profile_picture = State()

@dp.callback_query_handler(Text(startswith="card_"))
async def card_manager(call: types.CallbackQuery, state: FSMContext):
    operation = call.data.split('_')[1]
    print(f'Found an operation: {operation}', file=sys.stderr)
    if operation == 'new.start':
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Отмена")

            await bot.send_message(chat_id = call.from_user.id,
            text = f"Введите свой никнейм:",
            reply_markup=keyboard)

            await state.set_state(CardSetup.nickname.state)
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

@dp.message_handler(lambda message: any([(len(message.text)>20), (len(message.text)<1), ('.' in message.text), ('/' in message.text), ('_' in message.text)]), state=CardSetup.nickname)
async def process_nickname_invalid(message: types.Message, state: FSMContext):
    return await message.answer(f'Неверный никнейм.\nИмя игрока не должно содержать символы "., /, _". Длина ника - от 1 до 20 символов.')
    await state.set_state(CardSetup.nickname.state)

"""
Создание новой карты
"""

@dp.message_handler(state=CardSetup.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    try:
        await state.update_data(nickname=message.text)
        data = await state.get_data()
        print(data['nickname'])
    except Exception as e:
        print(f'Found an exception at process_nickname data parse: {e}', file=sys.stderr)

    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE (nickname = '{message.text}');"
    cursor.execute(sql)
    overlapping_users = cursor.fetchall()
    cursor.close()
    if len(overlapping_users) >= 1:
        await message.answer(f"Уже имеется пользователь с таким именем. Введите другой никнейм:")
        await state.set_state(CardSetup.nickname.state)
    else:
        await message.answer(f"Теперь добавьте изображение профиля:")
        await state.set_state(CardSetup.profile_picture.state)

@dp.message_handler(content_types=["photo"], state=CardSetup.profile_picture)
async def process_profile_picture(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        nickname = data['nickname']
        print(nickname)
        await message.photo[-1].download(destination_file=f"/~/BonchMafia/bot/pictures/profile/{nickname}.png", make_dirs=True)
        await state.finish()
        cursor = conn.cursor()
        sql = f"INSERT INTO users(userid, don, mafia, sheriff, citizen, won, lost, mentor, nickname) VALUES ({message.from_user.id}, 0, 0, 0, 0, 0, 0, '-', '{data['nickname']}');"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Главное меню"]
        keyboard.add(*buttons)
        await message.answer(f"Ваша карта была успешно добавлена. Приятных игр!", reply_markup=keyboard)
    except Exception as e:
        print(f"Found an exception in process_profile_picture: {e}", file=sys.stderr)