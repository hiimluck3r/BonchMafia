import sys
import psycopg2
import random
import aiogram.utils.markdown as fmt

from bot.dispatcher import dp, bot
from bot.controllers import *
from aiogram import types
from time import sleep
from bot import DB, USER, PASSWORD, HOST, ADMIN
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

"""
Подключение к БД
"""
flag = True
adminids = [ADMIN]
while flag:
    try:
        conn = psycopg2.connect(dbname=DB, user=USER, password=PASSWORD, host=HOST) #указывать в .env
        print('Connection to database is established')
        flag = False

        cursor = conn.cursor()
        sql = f"SELECT * FROM admins;"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()

        for row in data:
            adminids.append(row[1])
        
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
    keyboard = get_main_menu()
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

        league = get_league(won, total)
        
        card_process(nickname, league, don, mafia, sheriff, citizen, won, lost, total, mentor)
        
        keyboard = get_card_menu()
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
            print(f'Found an exception at card_manager.new.start option: {e}', file=sys.stderr)
    else:
        print(f'Found unresolved operation at card_manager: {operation}', file=sys.stderr)
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
    sql = f"SELECT COUNT(*) FROM users WHERE (nickname = '{message.text}');"
    cursor.execute(sql)
    overlapping_users = cursor.fetchone()[0]
    cursor.close()
    if overlapping_users >= 1:
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
        keyboard = goto_menu()
        await message.answer(f"Ваша карта была успешно добавлена. Приятных игр!", reply_markup=keyboard)
    except Exception as e:
        print(f"Found an exception at process_profile_picture: {e}", file=sys.stderr)


"""
Команды администрации
"""
class Mentor(StatesGroup):
    student_name = State()
    mentor_name = State()

class Notify(StatesGroup):
    notification_text = State()
    poster = State()

class GameProtocol(StatesGroup):
    gamedate = State()
    gamehost = State()
    player_1 = State()
    player_2 = State()
    player_3 = State()
    player_4 = State()
    player_5 = State()
    player_6 = State()
    player_7 = State()
    player_8 = State()
    player_9 = State()
    player_10 = State()
    winner = State()

def nickname_checker(nickname):
    cursor = conn.cursor()
    sql = f"SELECT COUNT(*) FROM users WHERE nickname = '{nickname}';"
    cursor.execute(sql)
    user_count = cursor.fetchone()[0]
    cursor.close()

    if user_count == 1:
        return True
    elif user_count == 0:
        return False
    else:
        print(f'why THE HELL do we have {user_count} {nickname}?????')
        return False
    

@dp.message_handler(commands="admin", chat_id=adminids)
async def admin_menu(message: types.Message):
    print(f"Admin logged: {message.from_user.id}", file=sys.stderr)
    keyboard = get_admin_menu()
    await message.answer(f"Админ меню", reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith="admin"), chat_id=adminids)
async def admin_query_handler(call: types.CallbackQuery, state: FSMContext):
    operation = call.data.split('_')[1]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    if operation == 'notify':
        await state.set_state(Notify.notification_text)
        await bot.send_message(chat_id=call.from_user.id, text="Введите никнейм наставника", reply_markup=keyboard)
    elif operation == 'mentor':
        await state.set_state(Mentor.student_name)
        await bot.send_message(chat_id=call.from_user.id, text="Введите никнейм ученика", reply_markup=keyboard)
    elif operation == 'game':
        await state.set_state(GameProtocol.gamedate)
        await bot.send_message(chat_id=call.from_user.id, text="Введите никнейм наставника", reply_markup=keyboard)
    
    await call.answer()

@dp.message_handler(state=Mentor.student_name)
async def process_student_name(message: types.Message, state: FSMContext):
    await state.update_data(student_name=message.text)
    data = await state.get_data()
    
    if nickname_checker(data['student_name']):
        await state.set_state(Mentor.mentor_name)
        await bot.send_message(chat_id=message.from_user.id, text="Введите никнейм наставника")
    else:
        await state.set_state(Mentor.student_name)
        await bot.send_message(chat_id=message.from_user.id, text=f"Пользователь {data['student_name']} не найден. Попробуйте ещё раз.")

@dp.message_handler(state=Mentor.mentor_name)
async def process_student_name(message: types.Message, state: FSMContext):
    await state.update_data(mentor_name=message.text)
    data = await state.get_data()

    if nickname_checker(data['mentor_name']):
        student = data['student_name']
        mentor = data['mentor_name']
        cursor = conn.cursor()
        sql = f"UPDATE users SET mentor = '{mentor}' WHERE nickname = '{student}';"
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        await state.finish()
        keyboard = goto_menu()
        await bot.send_message(chat_id=message.from_user.id, text="Наставник изменён.", reply_markup=keyboard)
    else:
        await state.set_state(Mentor.mentor_name)
        await bot.send_message(chat_id=message.from_user.id, text=f"Пользователь {data['student_name']} не найден. Попробуйте ещё раз.")