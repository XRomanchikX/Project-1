from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from google.oauth2.service_account import Credentials
import buttons
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

global user
user = {} # база пользователей

BOT_TOKEN = '5751694717:AAEkmL0Os01qZgbqCJ_K8i7USDMXUgfQe5g'

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('account.json')
client = gspread.authorize(credentials.with_scopes(scope))
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1B5YxE55su5tdpmjXminkjVY_DyWPuMbffoP7U1abxf8/edit#gid=636993454')
worksheet = sheet.get_worksheet(0)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class States(StatesGroup):
    LOCATION = State() 
    RADIUS = State()
    TOVAR = State()

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_select_product = types.KeyboardButton("Выбрать товар")
    button_search_product = types.KeyboardButton("Поиск товара")
    markup.add(button_select_product, button_search_product)
    await message.answer(f"Привет!\nВыбери опцию:",reply_markup=markup)

@dp.message_handler(text="Выйти",state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_select_product = types.KeyboardButton("Выбрать товар")
    button_search_product = types.KeyboardButton("Поиск товара")
    markup.add(button_select_product, button_search_product)
    await message.answer(f"Привет!\nВыбери опцию:",reply_markup=markup)

@dp.message_handler(text="Поиск товара")
async def cmd_search(message: types.Message):
    global user
    id = message.from_user.id
    user[f"all_cites_{id}"] = None
    user[f"cites_{id}"] = []
    user[f"city_{id}"] = 0
    user[f"radius_{id}"] = 0
    user[f"city_in_radius_{id}"] = []
    user[f"row_{id}"] = 0
    user[f"num_city_{id}"] = -1
    user[f"col_index_{id}"] = 0
    user[f"city_number_{id}"] = 0
    user[f"index_city_{id}"] = 0
    user[f"product_1_{id}"] = []
    user[f"adress_{id}"] = 2
    user[f"product_{id}"] = 0
    user[f"have_{id}"] = 2
    user[f"list_products_{id}"] = 1
    user[f"location_message_id_{id}"] = False
    user[f"tovar_{id}"] = None
    user[f"latitude_{id}"] = None
    user[f"longitude_{id}"] = None
    user[f"citys_{id}"] = None
    user[f"number_{id}"] = 1
    id = message.from_user.id
    user[f"product_1_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    catalog_str = "\n".join(user[f"product_1_{id}"])
    response = f"Список товаров:\n{catalog_str}"
    await message.reply(response)

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_input = message.text
    id = message.from_user.id
    user[f"product_1_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"product_1_{id}"] = [item.lower() for item in user[f"product_1_{id}"]]
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    keyboard = types.InlineKeyboardMarkup()
    if user_input.lower() in user[f"product_1_{id}"]:
        callback_data = f'select_product_{user_input}'
        keyboard.add(types.InlineKeyboardButton(text=user_input, callback_data=callback_data))
        await message.reply(f"Информация о товаре {user_input}: В наличии!\nПодтвердите товар нажав на кнопку.", reply_markup=keyboard)

@dp.message_handler(text="Выбрать товар")
async def command(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await state.finish()
    await States.TOVAR.set()
    global user
    user[f"all_cites_{id}"] = None
    user[f"cites_{id}"] = []
    user[f"city_{id}"] = 0
    user[f"radius_{id}"] = 0
    user[f"city_in_radius_{id}"] = []
    user[f"row_{id}"] = 0
    user[f"num_city_{id}"] = -1
    user[f"col_index_{id}"] = 0
    user[f"city_number_{id}"] = 0
    user[f"index_city_{id}"] = 0
    user[f"product_1_{id}"] = []
    user[f"adress_{id}"] = 2
    user[f"product_{id}"] = 0
    user[f"have_{id}"] = 2
    user[f"list_products_{id}"] = 1
    user[f"location_message_id_{id}"] = False
    user[f"tovar_{id}"] = None
    user[f"latitude_{id}"] = None
    user[f"longitude_{id}"] = None
    user[f"citys_{id}"] = None
    user[f"number_{id}"] = 1
    keyboard = types.InlineKeyboardMarkup()
    user[f"product_1_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)

    print(user[f"product_1_{id}"])
    for i in range(5):
        if user[f"product_1_{id}"][user[f"product_{id}"]] != None:
            callback_data = f'select_product_{user[f"product_1_{id}"][user[f"product_{id}"]]}'
            keyboard.add(types.InlineKeyboardButton(text=user[f"product_1_{id}"][user[f"product_{id}"]], callback_data=callback_data))
            user[f"product_{id}"] += 1
        else:
            break
    inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1')
    inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2')
    keyboard.add(inline_btn1, inline_btn2)
    message = (f'Ассортимент | страница {user[f"list_products_{id}"]}')
    await bot.send_message(int(id), message, reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn2", state=States.TOVAR)
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    global user
    id = callback_query.from_user.id
    try:
        print('+1:',user[f"product_{id}"],end=' | ')
        user[f"list_products_{id}"] += 1
        inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1')
        inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2')
        if user[f"product_{id}"] <= 1:
            user[f"product_{id}"] = 2
        for i in range(user[f"product_{id}"], user[f"product_{id}"] + 5):
            if i < len(user[f"product_1_{id}"]) and user[f"product_1_{id}"][i] != '':
                user[f"product_{id}"] += 1
                callback_data = f'select_product_{user[f"product_1_{id}"][i]}'
                keyboard.add(types.InlineKeyboardButton(text=user[f"product_1_{id}"][i], callback_data=callback_data))
        print('+2:',user[f"product_{id}"])
        if user[f"product_{id}"] >= len(user[f"product_1_{id}"]):
            raise IndexError
        await callback_query.message.edit_text(f'Ассортимент | страница {user[f"list_products_{id}"]}', reply_markup=keyboard.row(inline_btn1, inline_btn2))
    except IndexError:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(InlineKeyboardButton('⏪', callback_data='btn1'))
        await callback_query.message.edit_text('Товары кончились', reply_markup=inline_kb)

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn1", state=States.TOVAR)
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    global user
    id = callback_query.from_user.id
    try:
        user[f"product_{id}"] = user[f"product_{id}"] - 5
        user[f"list_products_{id}"] -= 1
        inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1')
        inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2')
        if user[f"product_{id}"] <= 1:
            user[f"product_{id}"] = 2
        if user[f"list_products_{id}"] > 0:
            for i in range(user[f"product_{id}"]-5, user[f"product_{id}"]):
                if i < len(user[f"product_1_{id}"]) and user[f"product_1_{id}"][i] != '':
                    callback_data = f'select_product_{user[f"product_1_{id}"][i]}'
                    keyboard.add(types.InlineKeyboardButton(text=user[f"product_1_{id}"][i], callback_data=callback_data))
            await callback_query.message.edit_text(f'Ассортимент | страница {user[f"list_products_{id}"]}', reply_markup=keyboard.row(inline_btn1, inline_btn2))
        else:
            raise IndexError
    except IndexError:
        user[f"product_{id}"] = 3
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(InlineKeyboardButton('⏩', callback_data='btn2'))
        await callback_query.message.edit_text('Товары кончились', reply_markup=inline_kb)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("select_product_"), state="*")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    global user
    id = callback_query.from_user.id
    user[f"tovar_{id}"] = str(callback_query.data[15:])
    col_index = worksheet.find(user[f"tovar_{id}"]).col
    user[f"citys_{id}"] = worksheet.col_values(3)
    haves = worksheet.col_values(col_index)
    for i in range(len(user[f"citys_{id}"])):
        if user[f"citys_{id}"][i] == None or user[f"citys_{id}"][i] == 'Адрес ТТ':
            pass
        if user[f"citys_{id}"][i] != None and user[f"citys_{id}"][i] != 'Адрес ТТ':
            if haves[i] == 'да':
                user[f"cites_{id}"].append(user[f"citys_{id}"][i])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_select_product = types.KeyboardButton("Выйти")
    markup.add(buttons.button4).add( button_select_product)
    await callback_query.message.answer(f'Выбран товар: {str(callback_query.data[15:])}\n\nОтправьте геолокацию', reply_markup=markup)
    await States.LOCATION.set()
@dp.message_handler(content_types=types.ContentType.LOCATION, state=States.LOCATION)
async def command(message: types.Message):
    global user
    id = message.from_user.id
    geolocator = Nominatim(user_agent="user")
    user[f"latitude_{id}"] = message.location.latitude
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_cancel_product = types.KeyboardButton("Выйти")
    markup.add(button_cancel_product)
    user[f"longitude_{id}"] = message.location.longitude
    await message.reply(f'Выбран адрес: {geolocator.reverse((user[f"latitude_{id}"],user[f"longitude_{id}"]))}\n\nТеперь введите радиус поиска (в метрах):', reply_markup=markup)
    await States.RADIUS.set()

@dp.message_handler(state=States.RADIUS)
async def command(message: types.Message, state: FSMContext):
    if message.text.isdigit() == False:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        button_cancel_product = types.KeyboardButton("Выйти")
        markup.add(button_cancel_product)
        await message.reply('Укажите число', reply_markup=markup)
    if message.text.isdigit() == True:
        #print(1)
        global user
        id = message.from_user.id
        chat_id = message.from_user.id
        geolocator = Nominatim(user_agent="user-chrome")
        user[f"radius_{id}"] = int(message.text)
        user[f"city_{id}"] = 0
        for i in range(len(user[f"cites_{id}"])):
            try:
                location = geolocator.geocode(user[f"cites_{id}"][i])
                shop_cord = (location.latitude,location.longitude)
                user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
                distance = geodesic(user_cord,shop_cord).meters
                if user[f"radius_{id}"] >= distance:
                    user[f"num_city_{id}"] = i
                    user[f"city_in_radius_{id}"].append(user[f"cites_{id}"][i])
                    print(user[f"cites_{id}"][i])
                    break
            except:
                pass
        location = geolocator.geocode(user[f"city_in_radius_{id}"][user[f"city_{id}"]])
        user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(inline_btn1, inline_btn2)
        shop_cord = (location.latitude,location.longitude)
        await bot.send_message(id,f'Товар: {user[f"tovar_{id}"]}\n\nНаходиться по адресу: {user[f"city_in_radius_{id}"][user[f"city_{id}"]]}\n\nНа расстоянии: {round(geodesic(user_cord,shop_cord).meters)} метрах от вас.', reply_markup=inline_kb)
        location_message = await bot.send_location(chat_id,location.latitude,location.longitude)
        user[f"location_message_id_{id}"] = location_message.message_id
        await state.finish()   

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn_next")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    global user
    id = callback_query.from_user.id
    await callback_query.message.edit_text(
            f'Ожидайте, идет поиск города')
    chat_id = callback_query.from_user.id
    geolocator = Nominatim(user_agent="user-chrome")
    user[f"city_{id}"] = user[f"city_{id}"] + 1
    user[f"city_number_{id}"] = 0
    try:  
        for i in range(user[f"num_city_{id}"]+1,len(user[f"cites_{id}"])):
            try:
                location = geolocator.geocode(user[f"cites_{id}"][i])
                shop_cord = (location.latitude,location.longitude)
                user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
                distance = geodesic(user_cord,shop_cord).meters
                if user[f"radius_{id}"] >= distance:
                    user[f"city_in_radius_{id}"].append(user[f"cites_{id}"][i])
                    user[f"num_city_{id}"] = i
                    print(user[f"cites_{id}"][i])
                    break   
            except:
                pass
    except:
            pass
    try:
        #print(+1)
        #print('city:', user[f"city_{id}"])
        location = geolocator.geocode(user[f"city_in_radius_{id}"][user[f"city_{id}"]])
        #print(2)
        user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
        #print(3)
        adress = user[f"city_in_radius_{id}"][user[f"city_{id}"]]
        #print(4)
        shop_cord = (location.latitude,location.longitude)
        #print(5)
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(inline_btn1, inline_btn2)
        if user[f"location_message_id_{id}"] != None:
            await bot.delete_message(chat_id, user[f"location_message_id_{id}"])
        #print(6)
        #print(shop_cord)
        await callback_query.message.edit_text(
            f'Товар: {user[f"tovar_{id}"]}\n\nНаходится по адресу: {adress}\n\nНа расстоянии: {round(geodesic(user_cord, shop_cord).meters)} метрах от вас.',reply_markup=inline_kb)
        location_message = await bot.send_location(chat_id, location.latitude, location.longitude)
        user[f"location_message_id_{id}"] = location_message.message_id
        await state.finish()
    except:
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(inline_btn1)
        await callback_query.message.edit_text('Это был последний ближайший магазин', reply_markup=inline_kb)
        return

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn_back")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(f'Ожидайте, идет поиск города')
    id = callback_query.from_user.id
    global user
    geolocator = Nominatim(user_agent="user-chrome")
    user[f"city_number_{id}"] = user[f"city_number_{id}"] + 1
    user[f"city_{id}"] = user[f"city_{id}"] - 1
    user[f"number_{id}"] = user[f"number_{id}"] + 1
    try:
        #print(-1)
        location = geolocator.geocode(user[f"city_in_radius_{id}"][-user[f"number_{id}"]])
        #print(2)
        user_cord = (user[f"latitude_{id}"], user[f"longitude_{id}"])
        #print(3)
        adress = user[f"city_in_radius_{id}"][-user[f"number_{id}"]]
        #print(4)
        shop_cord = (location.latitude, location.longitude)
        #print(5)
        radius = geodesic(user_cord, shop_cord).meters
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(inline_btn1, inline_btn2)
        #print(radius)
        r_radius = round(radius)
        #print(adress)
        if user[f"location_message_id_{id}"] != None:
            await bot.delete_message(id, user[f"location_message_id_{id}"])
        #print(6)
        await callback_query.message.edit_text(f'Товар: {user[f"tovar_{id}"]}\n\nНаходится по адресу: {adress}\n\nНа расстоянии: {r_radius} метрах от вас',reply_markup=inline_kb)
        #print(7)
        location_message = await bot.send_location(id, location.latitude, location.longitude)
        #print(8)
        user[f"location_message_id_{id}"] = location_message.message_id
        #print(9)
    except:
        user[f"city_{id}"] = -1
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(inline_btn2)
        await callback_query.message.edit_text('Это был первый ближайший магазин', reply_markup=inline_kb)
        return
    await state.finish()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
