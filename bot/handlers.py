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
async def my_card(message: types.Message):
    userid = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE userid={userid}")
    userstats = cursor.fetchone()
    cursor.close()
    if userstats is None:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Создать новую карту", callback_data="card_new.start"))
        await message.answer("Похоже, у вас нет карты.", reply_markup=keyboard)
    else:
        userid = userstats[1]
        don = userstats[2]
        don_total = userstats[3]
        mafia = userstats[4]
        mafia_total = userstats[5]
        sheriff = userstats[6]
        sheriff_total = userstats[7]
        citizen = userstats[8]
        citizen_total = userstats[9]
        won = userstats[10]
        lost = userstats[11]
        total = won+lost
        mentor = userstats[12]
        nickname = userstats[13]

        league = get_league(won, total)
        
        card_process(nickname, league, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, total, mentor)
        
        keyboard = get_card_menu()
        card_photo = open(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png", 'rb')
        await message.answer_photo(card_photo, reply_markup=keyboard,
        caption="Ваша карта")

class OtherCard(StatesGroup):
    nickname = State()

@dp.message_handler(Text(equals="Другой игрок"))
async def else_card(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    await message.answer("Введите имя пользователя, карту которого хотите посмотреть:", reply_markup=keyboard)
    await state.set_state(OtherCard.nickname.state)

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


@dp.message_handler(state=OtherCard.nickname)
async def process_else_card(message: types.Message, state: FSMContext):
    try:
        await state.update_data(nickname=message.text)
        data = await state.get_data()
    except Exception as e:
        print(f'Found an exception at else_card data parse: {e}', file=sys.stderr)
    
    await state.finish()

    nickname = data['nickname']
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE nickname='{nickname}'")
    userstats = cursor.fetchone()
    cursor.close()
    if userstats is None:
        await message.answer("Похоже, что такого игрока нет.", reply_markup=goto_menu())
    else:
        userid = userstats[1]
        don = userstats[2]
        don_total = userstats[3]
        mafia = userstats[4]
        mafia_total = userstats[5]
        sheriff = userstats[6]
        sheriff_total = userstats[7]
        citizen = userstats[8]
        citizen_total = userstats[9]
        won = userstats[10]
        lost = userstats[11]
        total = won+lost
        mentor = userstats[12]
        nickname = userstats[13]

        league = get_league(won, total)
        
        card_process(nickname, league, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, total, mentor)
        
        card_photo = open(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png", 'rb')
        await message.answer_photo(card_photo, reply_markup=goto_menu(),
        caption=f"Карта {nickname}")

"""
Создание новой карты
"""

@dp.message_handler(state=CardSetup.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    try:
        await state.update_data(nickname=message.text)
        data = await state.get_data()
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
        print('Found new player: ', nickname)

        with open(f"/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png", "wb") as profile_photo:
            await message.photo[-1].download(destination_file=profile_photo)
        profile_circular_process(nickname)

        await state.finish()
        cursor = conn.cursor()
        sql = f"INSERT INTO users(userid, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, mentor, nickname) VALUES ({message.from_user.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', '{data['nickname']}');"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        keyboard = goto_menu()
        await message.answer(f"Ваша карта была успешно добавлена. Приятных игр!", reply_markup=keyboard)
    except Exception as e:
        print(f"Found an exception at process_profile_picture: {e}", file=sys.stderr)

"""
Изменение никнейма пользователя
"""
class ChangeNickname(StatesGroup):
    nickname = State()

class ChangePicture(StatesGroup):
    photo = State()

@dp.message_handler(Text(equals="Изменить никнейм"))
async def change_nickname(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    await message.answer(f"Введите новый никнейм:", reply_markup=keyboard)

    await state.set_state(ChangeNickname.nickname.state)


@dp.message_handler(lambda message: any([(len(message.text)>20), (len(message.text)<1), ('.' in message.text), ('/' in message.text), ('_' in message.text)]), state=ChangeNickname.nickname)
async def process_changed_nickname_invalid(message: types.Message, state: FSMContext):
    return await message.answer(f'Неверный никнейм.\nИмя игрока не должно содержать символы "., /, _". Длина ника - от 1 до 20 символов.')
    await state.set_state(ChangeNickname.finisher.state)

@dp.message_handler(state=ChangeNickname.nickname)
async def process_changed_nickname(message: types.Message, state: FSMContext):
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
    if overlapping_users >= 1:
        cursor.close()
        await message.answer(f"Уже имеется пользователь с таким именем. Введите другой никнейм:")
        await state.set_state(CardSetup.nickname.state)
    else:
        sql = f"SELECT * FROM users WHERE userid = {message.from_user.id};"
        cursor.execute(sql)
        nickname = cursor.fetchone()[-1]
        await message.answer(f"Имя пользователя изменено.", reply_markup=goto_menu())
        sql = f"UPDATE users SET nickname = '{data['nickname']}' WHERE userid = {message.from_user.id};"
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        old_photo_name = f"/~/BonchMafia/bot/pictures/profile/{nickname}.png"
        new_photo_name = f"/~/BonchMafia/bot/pictures/profile/{data['nickname']}.png"

        os.rename(old_photo_name, new_photo_name)
        await state.finish()

"""
Изменение аватарки пользователя
"""  

@dp.message_handler(Text(equals="Изменить изображение"))
async def change_profile_picture(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    await message.answer(f"Пришлите новое изображение профиля:", reply_markup=keyboard)

    await state.set_state(ChangePicture.photo.state)

@dp.message_handler(content_types=["photo"], state=ChangePicture.photo)
async def process_changed_profile_picture(message: types.Message, state: FSMContext):
    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE userid = {message.from_user.id};"
    cursor.execute(sql)
    nickname = cursor.fetchone()[-1]
    cursor.close()

    await message.photo[-1].download(destination_file=f"/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png")
    profile_circular_process(nickname)

    await state.finish()
    await message.answer("Изображение профиля изменено.", reply_markup=goto_menu())


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
    don = State()
    sheriff = State()
    mafia = State()
    citizen = State()
    winner = State()

def nickname_checker(nickname):
    if nickname == "blank":
        return True

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
        await bot.send_message(chat_id=call.from_user.id, text="Notify", reply_markup=keyboard)
    elif operation == 'mentor':
        await state.set_state(Mentor.student_name)
        await bot.send_message(chat_id=call.from_user.id, text="Введите никнейм ученика:", reply_markup=keyboard)
    elif operation == 'game':
        await state.set_state(GameProtocol.gamedate)
        await bot.send_message(chat_id=call.from_user.id, text="Введите точную дату игры:", reply_markup=keyboard)
    
    await call.answer()

"""
Назначение наставника
"""

@dp.message_handler(state=Mentor.student_name)
async def process_student_name(message: types.Message, state: FSMContext):
    await state.update_data(student_name=message.text)
    data = await state.get_data()
    
    if nickname_checker(data['student_name']):
        await state.set_state(Mentor.mentor_name)
        await message.answer(f"Введите никнейм наставника:")
    else:
        await state.set_state(Mentor.student_name)
        await message.answer(f"Пользователь {data['student_name']} не найден. Попробуйте ещё раз.")

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
        await message.answer(f"Наставник изменён.", reply_markup=keyboard)
    else:
        await state.set_state(Mentor.mentor_name)
        await message.answer(f"Пользователь {data['student_name']} не найден. Попробуйте ещё раз.")

"""
Внесение игрового протокола
"""
#current_state = await state.get_state()

@dp.message_handler(state=GameProtocol.gamedate)
async def process_gamedate(message: types.Message, state: FSMContext):
    await state.update_data(gamedate=message.text)

    await state.set_state(GameProtocol.gamehost)
    await message.answer("Введите ник ведущего:")

@dp.message_handler(state=GameProtocol.gamehost)
async def process_host(message: types.Message, state: FSMContext):
    await state.update_data(gamehost=message.text)

    await state.set_state(GameProtocol.don)
    await message.answer("Введите никнейм дона:")

@dp.message_handler(state=GameProtocol.don)
async def process_don(message: types.Message, state: FSMContext):
    if nickname_checker(message.text):
        await state.update_data(don=message.text)
        await state.set_state(GameProtocol.sheriff)
        await message.answer("Введите никнейм шерифа:")
    else:
        await message.answer(f"Пользователь не найден. Попробуйте ещё раз.")
        await state.set_state(GameProtocol.don)

@dp.message_handler(state=GameProtocol.sheriff)
async def process_sheriff(message: types.Message, state: FSMContext):
    if nickname_checker(message.text):
        await state.update_data(sheriff=message.text)
        await state.set_state(GameProtocol.mafia)
        await message.answer("Введите никнеймы оставшихся 2 мафий через точку (пример dflt.Кринж):")
    else:
        await message.answer(f"Пользователь не найден. Попробуйте ещё раз.")
        await state.set_state(GameProtocol.sheriff)

@dp.message_handler(state=GameProtocol.mafia)
async def process_mafia(message: types.Message, state: FSMContext):
    mafia = message.text.split('.')

    for nickname in mafia:
        if nickname_checker(nickname) and len(mafia)==2:
            pass
        elif len(mafia)!=2:
            await message.answer(f"Неверно заданы пользователи. Указанное количество пользователей: {len(mafia)}")
            return await state.set_state(GameProtocol.mafia)
        else:
            await message.answer(f"Пользователь {nickname} не найден. Попробуйте ещё раз.")
            return await state.set_state(GameProtocol.mafia)

    await state.update_data(mafia=mafia)

    await state.set_state(GameProtocol.citizen)
    await message.answer("Введите никнеймы мирных игроков (пример dflt.Кринж... 7 игроков):")

@dp.message_handler(state=GameProtocol.citizen)
async def process_citizen(message: types.Message, state: FSMContext):
    citizen = message.text.split('.')

    for nickname in citizen:
        if nickname_checker(nickname) and len(citizen)==7:
            pass
        elif len(citizen)!=7:
            await message.answer(f"Неверно заданы пользователи. Указанное количество пользователей: {len(citizen)}")
            return await state.set_state(GameProtocol.citizen)
        else:
            await message.answer(f"Пользователь {nickname} не найден. Попробуйте ещё раз.")
            return await state.set_state(GameProtocol.citizen)

    await state.update_data(citizen=citizen)

    await state.set_state(GameProtocol.winner)
    await message.answer("Введите победившую команду (К или Ч, где К - Красные, Ч - Чёрные):")

@dp.message_handler(state=GameProtocol.winner)
async def process_winner(message: types.Message, state: FSMContext):
    if message.text.lower() == 'ч' or message.text.lower()=='к':
        keyboard = goto_menu()
        await state.update_data(winner=message.text.lower())
        data = await state.get_data()
        await state.finish()

        mafia = '.'.join(data['mafia'])
        citizen = '.'.join(data['citizen'])

        cursor = conn.cursor()
        sql = f"INSERT INTO games(gamedate, gamehost, don, sheriff, mafia, citizen, winner) VALUES ('{data['gamedate']}', '{data['gamehost']}', '{data['don']}', '{data['sheriff']}', '{mafia}', '{citizen}', '{data['winner']}');"
        cursor.execute(sql)

        if data['winner']=='ч':
            sql = f"UPDATE users SET don = don+1 WHERE nickname = '{data['don']}';"
            cursor.execute(sql)
            sql = f"UPDATE users SET won = won+1 WHERE nickname = '{data['don']}';"
            cursor.execute(sql)

            for nickname in data['mafia']:
                sql = f"UPDATE users SET mafia = mafia+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)
                sql = f"UPDATE users SET won = won+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)

            
            sql = f"UPDATE users SET lost = lost+1 WHERE nickname = '{data['sheriff']}';"
            cursor.execute(sql)

            for nickname in data['citizen']:
                sql = f"UPDATE users SET lost = lost+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)

        else:
            sql = f"UPDATE users SET lost = lost+1 WHERE nickname = '{data['don']}';"
            cursor.execute(sql)

            for nickname in data['mafia']:
                sql = f"UPDATE users SET lost = lost+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)

            sql = f"UPDATE users SET sheriff = sheriff+1 WHERE nickname = '{data['sheriff']}';"
            cursor.execute(sql)
            sql = f"UPDATE users SET won = won+1 WHERE nickname = '{data['sheriff']}';"
            cursor.execute(sql)

            for nickname in data['citizen']:
                sql = f"UPDATE users SET citizen = citizen+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)
                sql = f"UPDATE users SET won = won+1 WHERE nickname = '{nickname}';"
                cursor.execute(sql)
        
        for nickname in data['mafia']:
            sql = f"UPDATE users SET mafia_total = mafia_total+1 WHERE nickname = '{nickname}'"
            cursor.execute(sql)
        
        for nickname in data['citizen']:
            sql = f"UPDATE users SET citizen_total = citizen_total+1 WHERE nickname = '{nickname}'"
            cursor.execute(sql)

        sql = f"UPDATE users SET don_total = don_total+1 WHERE nickname = '{data['don']}'"
        cursor.execute(sql)

        sql = f"UPDATE users SET sheriff_total = sheriff_total+1 WHERE nickname = '{data['sheriff']}'"
        cursor.execute(sql)
        
        conn.commit()
        cursor.close()
        await message.answer("Игра записана.", reply_markup=keyboard)
    else:
        await state.set_state(GameProtocol.winner)
        await message.answer("Неверно указан победитель. Укажите 'К', если победили красные и 'Ч', если победили чёрные.")

"""
Объявления
"""

"""
Редактировать админов (root only)
"""
@dp.message_handler(commands="admadd", chat_id=ADMIN)
async def admin_add(message: types.Message):
    global adminids

    arguments = message.get_args().split('.')
    adminids.append(int(arguments[0]))
    cursor = conn.cursor()
    sql = f"INSERT INTO admins (userid, nickname) VALUES ({int(arguments[0])}, '{arguments[1]}');"
    conn.commit()
    cursor.close()
    await message.reply(f"Админ @{await get_username(int(arguments[0]))} добавлен.")

@dp.message_handler(commands="admrm", chat_id=ADMIN)
async def admin_remove(message: types.Message):
    arguments = message.get_args()
    global adminids

    adminid.remove(arguments)
    cursor = conn.cursor()
    sql = f"DELETE FROM admins WHERE userid = {arguments};"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    await message.reply(f"Админ @{await get_username(arguments)} удалён.")

@dp.message_handler(commands="admlook", chat_id=ADMIN)
async def admin_look(message: types.Message):
    text = ''

    global adminids
    for admin in adminids:
        text += f"{str(admin)} - @{await get_username(admin)}\n"
    await message.answer(text)

@dp.message_handler(commands="id")
async def get_my_id(message: types.Message):
    await message.answer(message.from_user.id)