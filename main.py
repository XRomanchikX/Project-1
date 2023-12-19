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
from urllib.parse import quote
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def lisst(in1 , list1, name):
    for i in range(len(in1)):
        if in1[i][0] == name:
            list1.append(in1[i])

global user
user = {} # база пользователей

BOT_TOKEN = '5751694717:AAEkmL0Os01qZgbqCJ_K8i7USDMXUgfQe5g'

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('account.json')
client = gspread.authorize(credentials.with_scopes(scope))
#sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1B5YxE55su5tdpmjXminkjVY_DyWPuMbffoP7U1abxf8/edit#gid=636993454')
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
    user[f"vse_naz_{id}"] = []
    user[f"vse_naz_in_radius_{id}"] = []
    user[f"city_{id}"] = 0
    user[f"radius_{id}"] = 0
    user[f"city_in_radius_{id}"] = []
    user[f"row_{id}"] = 0
    user[f"num_city_{id}"] = -1
    user[f"col_index_{id}"] = 0
    user[f"city_number_{id}"] = 0
    user[f"index_city_{id}"] = 0
    user[f"product_1_{id}"] = []
    user[f"set_1_{id}"] = []
    user[f"set_2_{id}"] = []
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
    response = f"Напишите название нужного товара так, как указано на офицальном сайте!\n\nПример:\nУстройство MINICAN 3 PRO\nКартридж MINICAN\nЖидкость SKALA"
    await message.reply(response)

@dp.message_handler(text="Выбрать товар")
async def command(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await state.finish()
    global user
    user[f"all_cites_{id}"] = None
    user[f"cites_{id}"] = []
    user[f"city_{id}"] = 0
    user[f"radius_{id}"] = 0
    user[f"city_in_radius_{id}"] = []
    user[f"vse_naz_{id}"] = []
    user[f"vse_naz_in_radius_{id}"] = []
    user[f"row_{id}"] = 0
    user[f"num_city_{id}"] = -1
    user[f"col_index_{id}"] = 0
    user[f"city_number_{id}"] = 0
    user[f"index_city_{id}"] = 0
    user[f"product_1_{id}"] = []
    user[f"set_1_{id}"] = []
    user[f"set_2_{id}"] = []
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
    user[f"vse_tovari_{id}"] = []
    user[f"katalog_{id}"] = None
    user[f"vse_tovar_{id}"] = []
    keyboard1 = types.InlineKeyboardMarkup()
    user[f"product_1_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    for i in range(len(user[f"product_1_{id}"])):
        new = user[f"product_1_{id}"][i].split(' ')
        user[f"vse_tovar_{id}"].append(new)
    keyboard1.row(types.InlineKeyboardButton(text='Жидкости', callback_data='kat_Жидкость'), types.InlineKeyboardButton(text='Устройства', callback_data='kat_Устройства'))
    keyboard1.row(types.InlineKeyboardButton(text='Бестобачная смесь', callback_data='kat_Бестобачная смесь'),types.InlineKeyboardButton(text='Табак', callback_data='kat_Табак'))
    keyboard1.row(types.InlineKeyboardButton(text='Испарители', callback_data='kat_Испарители'),types.InlineKeyboardButton(text='Катриджи', callback_data='kat_Катридж'))
    keyboard1.row(types.InlineKeyboardButton(text='Однаразки', callback_data='kat_Однаразки'),types.InlineKeyboardButton(text='Жевательный табак', callback_data='kat_Жевательный табак'))
    await bot.send_message(id, f'Каталог', reply_markup=keyboard1)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("kat_"), state="*")
async def process_another_callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.from_user.id
    global user
    le_2 = callback_query.data[4:].split(' ')
    if len(le_2) > 1:
        user[f"katalog_{id}"] = le_2[0]
    if len(le_2) == 1:
        user[f"katalog_{id}"] = callback_query.data[4:]
    lisst(user[f"vse_tovar_{id}"],user[f"vse_tovari_{id}"],user[f"katalog_{id}"])
    #debug print(user[f"vse_tovari_{id}"])
    for i in range(len(user[f"vse_tovari_{id}"])):
        pass
    keyboard = InlineKeyboardMarkup()
    try:
        inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1') #but1
        inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2') #but2
        if user[f"product_{id}"] < 0: # проверка на первый товар
            user[f"product_{id}"] = 0
        for i in range(5):
            try:
                callback_data = f'select_product_{" ".join(user[f"vse_tovari_{id}"][i])}'
                keyboard.add(types.InlineKeyboardButton(text=" ".join(user[f"vse_tovari_{id}"][i]), callback_data=callback_data))
            except:
                pass
        await callback_query.message.edit_text(f'Ассортимент | страница {user[f"list_products_{id}"]}', reply_markup=keyboard.row(inline_btn1, inline_btn2))
    except:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(InlineKeyboardButton('⏪', callback_data='btn1'))
        await callback_query.message.edit_text('Товары кончились', reply_markup=inline_kb)

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn2")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    def bn(num:int):
        callback_data = f'select_product_{" ".join(user[f"vse_tovari_{id}"][num])}'
        keyboard.add(types.InlineKeyboardButton(text=" ".join(user[f"vse_tovari_{id}"][num]), callback_data=callback_data))
    await bot.answer_callback_query(callback_query.id)
    global user
    id = callback_query.from_user.id
    try:
        #debug print('+1:',user[f"product_{id}"],end=' | ')
        user[f"list_products_{id}"] += 1
        user[f"product_{id}"] += 5
        inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1')
        inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2')
        #debug print(user[f"vse_tovari_{id}"])
        nnn = len(user[f"vse_tovari_{id}"])
        if nnn >= 6:
            for i in range(user[f"product_{id}"], user[f"product_{id}"] + 5):
                try:
                    callback_data = f'select_product_{" ".join(user[f"vse_tovari_{id}"][i])}'
                    keyboard.add(types.InlineKeyboardButton(text=" ".join(user[f"vse_tovari_{id}"][i]), callback_data=callback_data))
                except:
                    pass
        else:
            try:
                bn(0)
                user[f"list_products_{id}"] = 1
            except:
                pass
            try:
                bn(1)
                user[f"list_products_{id}"] = 1
            except:
                pass
            try:
                bn(2)
                user[f"list_products_{id}"] = 1
            except:
                pass
            try:
                bn(3)
                user[f"list_products_{id}"] = 1
            except:
                pass
            try:
                bn(4)
                user[f"list_products_{id}"] = 1
            except:
                pass
        #debug print('+2:',user[f"product_{id}"])
        try:
            keyboard['inline_keyboard'][0]
        except:
            raise IndexError
        try:
            await callback_query.message.edit_text(f'Ассортимент | страница {user[f"list_products_{id}"]}', reply_markup=keyboard.row(inline_btn1, inline_btn2))
        except:
            raise IndexError
    except IndexError:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(InlineKeyboardButton('⏪', callback_data='btn1'))
        await callback_query.message.edit_text('Товары кончились', reply_markup=inline_kb)

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn1")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    await bot.answer_callback_query(callback_query.id)
    global user
    id = callback_query.from_user.id
    try:
        #debug print('-1:',user[f"product_{id}"],end=' | ')
        user[f"product_{id}"] = user[f"product_{id}"] - 10
        #debug print('-2:',user[f"product_{id}"],end=' | ')
        user[f"list_products_{id}"] -= 1
        if user[f"product_{id}"] <= 0:
            user[f"product_{id}"] = 0
            user[f"list_products_{id}"] = 1
        #debug print('-3:',user[f"product_{id}"])
        inline_btn1 = InlineKeyboardButton('⏪', callback_data='btn1')
        inline_btn2 = InlineKeyboardButton('⏩', callback_data='btn2')
        for i in range(user[f"product_{id}"], user[f"product_{id}"]+5):
            try:
                callback_data = f'select_product_{" ".join(user[f"vse_tovari_{id}"][i])}'
                keyboard.add(types.InlineKeyboardButton(text=" ".join(user[f"vse_tovari_{id}"][i]), callback_data=callback_data))
            except:
                pass
        try:
            await callback_query.message.edit_text(f'Ассортимент | страница {user[f"list_products_{id}"]}', reply_markup=keyboard.row(inline_btn1, inline_btn2))
        except:
            raise IndexError
    except IndexError:
        user[f"product_{id}"] = 0
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(InlineKeyboardButton('⏩', callback_data='btn2')) 
        await callback_query.message.edit_text('Товары кончились', reply_markup=inline_kb)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("select_product_"), state="*")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    global user
    id = callback_query.from_user.id
    user[f"tovar_{id}"] = str(callback_query.data[15:])
    col_index = worksheet.find(user[f"tovar_{id}"]).col
    user[f"citys_{id}"] = worksheet.col_values(3)
    haves = worksheet.col_values(col_index)
    user[f"set_1_{id}"] = worksheet.col_values(2)
    for i in range(len(user[f"citys_{id}"])):
        if user[f"citys_{id}"][i] == None or user[f"citys_{id}"][i] == 'Адрес ТТ':
            pass
        if user[f"citys_{id}"][i] != None and user[f"citys_{id}"][i] != 'Адрес ТТ':
            if haves[i] == 'да':
                user[f"set_2_{id}"].append(user[f"set_1_{id}"][i])
                user[f"cites_{id}"].append(user[f"citys_{id}"][i])
    ##debug print(user[f"cites_{id}"])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_select_product = types.KeyboardButton("Выйти")
    markup.add(buttons.button4).add( button_select_product)
    await callback_query.message.answer(f'Выбран товар: {str(callback_query.data[15:])}\n\nОтправьте геолокацию', reply_markup=markup)
    await States.LOCATION.set()
@dp.message_handler(content_types=types.ContentType.LOCATION, state=States.LOCATION)
async def command(message: types.Message, state: FSMContext):
    id = message.from_user.id
    global user
    known_cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Нижний Новгород','Казань', 'Самара', 'Омск', 'Челябинск', 'Ростов-на-Дону', 'Уфа', 'Волгоград','Пермь', 'Красноярск', 'Воронеж', 'Саратов', 'Краснодар', 'Тольятти', 'Барнаул','Кудрово', 'Колпино', 'Мурино', 'Гатчина', 'Шушары', 'Кронштадт', 'Сосновый бор', 'Петергоф', 'Выборг', 'Пушкин', 'Красное Село', 'Ломоносов','Петрозаводск']
    geolocator = Nominatim(user_agent="user")
    location = geolocator.reverse(f'{message.location.latitude},{message.location.longitude}')
    loc_dict = location.raw
    user_city = loc_dict['address']['city'].split(' ')
    us_city = '' #!
    for i in range(len(user_city)):
        if user_city[i] in known_cities:
            user_city.append(user_city[i])
            us_city = user_city[-1]
            break
        try:
            user_city[i+1]
        except:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            button_cancel_product = types.KeyboardButton("Выйти")
            markup.add(button_cancel_product)
            await bot.send_message(id, f'Увы! Вашего города нету в базе', reply_markup=markup)
            await state.finish()
            return 1
    prosto_city = []
    in_city = []
    for i in range(len(user[f"cites_{id}"])):
        new = user[f"cites_{id}"][i].split(', ')
        prosto_city.append(new)
    user[f"cites_{id}"] = prosto_city
    lisst(user[f"cites_{id}"],in_city, us_city)
    user[f"cites_{id}"] = in_city
    formatted_addresses = [' '.join(address) for address in user[f"cites_{id}"]]
    user[f"cites_{id}"] = formatted_addresses
    #debug print(user[f"cites_{id}"])
    user[f"latitude_{id}"] = message.location.latitude
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button_cancel_product = types.KeyboardButton("Выйти")
    markup.add(button_cancel_product)
    user[f"longitude_{id}"] = message.location.longitude
    await message.reply(f'Выбран адрес: {geolocator.reverse((user[f"latitude_{id}"],user[f"longitude_{id}"]))}\n\nТеперь введите радиус поиска (в метрах):', reply_markup=markup)
    await States.RADIUS.set()

@dp.message_handler(state=States.RADIUS)
async def command(message: types.Message, state: FSMContext):
    if message.text.isdigit() != True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        button_cancel_product = types.KeyboardButton("Выйти")
        markup.add(button_cancel_product)
        await message.reply('Укажите число', reply_markup=markup)
    if message.text.isdigit() == True:
        ##debug print(1)
        global user
        id = message.from_user.id
        chat_id = message.from_user.id
        location_message = await bot.send_message(id,f'Идет поиск магазина!')
        wait_city = location_message.message_id
        geolocator = Nominatim(user_agent="user-chrome")
        user[f"radius_{id}"] = int(message.text)
        user[f"city_{id}"] = 0
        kol_raz = 0
        for i in range(len(user[f"cites_{id}"])):
            try:
                location = geolocator.geocode(user[f"cites_{id}"][i])
                shop_cord = (location.latitude,location.longitude)
                user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
                distance = geodesic(user_cord,shop_cord).meters
                kol_raz += 1
                if user[f"radius_{id}"] >= distance:
                    user[f"num_city_{id}"] = i
                    user[f"vse_naz_in_radius_{id}"].append(user[f"set_2_{id}"][i])
                    user[f"city_in_radius_{id}"].append(user[f"cites_{id}"][i])
                    #debug print(user[f"cites_{id}"][i])
                    break
                if user[f"radius_{id}"] < distance and kol_raz >= 20:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                    button_cancel_product = types.KeyboardButton("Выйти")   
                    markup.add(button_cancel_product)
                    await state.finish()
                    await bot.send_message(id, f'Увы! В данном радиусе ничего не нашлось', reply_markup=markup)
                    break
            except:
                pass
        try:
            test = user[f"city_in_radius_{id}"][0].replace(' ', ', ')
            set_in_adress = worksheet.row_values(worksheet.find(f"{test}").row)
            location = geolocator.geocode(user[f"city_in_radius_{id}"][user[f"city_{id}"]])
            user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
            inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
            inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
            inline_kb = InlineKeyboardMarkup(row_width=2)
            inline_kb.add(inline_btn1, inline_btn2)
            shop_cord = (location.latitude,location.longitude)
            if wait_city != None:
                await bot.delete_message(id, wait_city)
            await bot.send_message(id,f'Товар: {user[f"tovar_{id}"]}\n\nНаходиться по адресу: {user[f"city_in_radius_{id}"][user[f"city_{id}"]]}\nСеть магазина: {set_in_adress[1]}\nНа расстоянии: {round(geodesic(user_cord,shop_cord).meters)} метрах от вас.', reply_markup=inline_kb)
            location_message = await bot.send_location(chat_id,location.latitude,location.longitude)
            user[f"location_message_id_{id}"] = location_message.message_id
            await state.finish()   
        except:
            pass
@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn_next")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    global user
    id = callback_query.from_user.id
    await callback_query.message.edit_text(
            f'Идет поиск магазина!')
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
                    user[f"vse_naz_in_radius_{id}"].append(user[f"set_2_{id}"][i])
                    user[f"city_in_radius_{id}"].append(user[f"cites_{id}"][i])
                    user[f"num_city_{id}"] = i
                    #debug print(user[f"cites_{id}"][i])
                    break   
            except:
                pass
    except:
            pass
    try:
        #debug #debug print(user[f"city_{id}"])
        #debug #debug print(user[f"city_in_radius_{id}"])
        #debug #debug print(user[f"city_in_radius_{id}"][user[f"city_{id}"]])
        test = user[f"city_in_radius_{id}"][user[f"city_{id}"]].replace(' ', ', ')
        ##debug print(1)
        set_in_adress = worksheet.row_values(worksheet.find(f"{test}").row)
        location = geolocator.geocode(user[f"city_in_radius_{id}"][user[f"city_{id}"]])
        #debug #debug print(2)
        user_cord = (user[f"latitude_{id}"],user[f"longitude_{id}"])
        #debug #debug print(3)
        adress = user[f"city_in_radius_{id}"][user[f"city_{id}"]]
        #debug #debug print(4)
        shop_cord = (location.latitude,location.longitude)
        #debug #debug print(5)
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(inline_btn1, inline_btn2)
        if user[f"location_message_id_{id}"] != None:
            await bot.delete_message(chat_id, user[f"location_message_id_{id}"])
        ##debug print(6)
        ##debug print(shop_cord)
        await callback_query.message.edit_text(
            f'Товар: {user[f"tovar_{id}"]}\n\nНаходится по адресу: {adress}\nСеть магазина: {set_in_adress[1]}\nНа расстоянии: {round(geodesic(user_cord, shop_cord).meters)} метрах от вас.',reply_markup=inline_kb)
        location_message = await bot.send_location(chat_id, location.latitude, location.longitude)
        user[f"location_message_id_{id}"] = location_message.message_id
        await state.finish()
        #debug #debug print(user[f"city_in_radius_{id}"])
    except:
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(inline_btn1)
        await callback_query.message.edit_text('Это был последний ближайший магазин', reply_markup=inline_kb)
        return

@dp.callback_query_handler(lambda callback_query: callback_query.data == "btn_back")
async def command(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(f'Идет поиск магазина!')
    id = callback_query.from_user.id
    global user
    geolocator = Nominatim(user_agent="user-chrome")
    user[f"city_number_{id}"] = user[f"city_number_{id}"] + 1
    user[f"city_{id}"] = user[f"city_{id}"] - 1
    user[f"number_{id}"] = user[f"number_{id}"] + 1
    try:
        ##debug print(-1)
        test = user[f"city_in_radius_{id}"][-user[f"number_{id}"]].replace(' ', ', ')
        ##debug print(1)
        set_in_adress = worksheet.row_values(worksheet.find(f"{test}").row)
        location = geolocator.geocode(user[f"city_in_radius_{id}"][-user[f"number_{id}"]])
        ##debug print(2)
        user_cord = (user[f"latitude_{id}"], user[f"longitude_{id}"])
        ##debug print(3)
        adress = user[f"city_in_radius_{id}"][-user[f"number_{id}"]]
        ##debug print(4)
        shop_cord = (location.latitude, location.longitude)
        ##debug print(5)
        radius = geodesic(user_cord, shop_cord).meters
        inline_btn1 = InlineKeyboardButton('<< Назад', callback_data='btn_back')
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(inline_btn1, inline_btn2)
        ##debug print(radius)
        r_radius = round(radius)
        ##debug print(adress)
        if user[f"location_message_id_{id}"] != None:
            await bot.delete_message(id, user[f"location_message_id_{id}"])
        ##debug print(6)
        await callback_query.message.edit_text(f'Товар: {user[f"tovar_{id}"]}\n\nНаходится по адресу: {adress}\nСеть магазина: {set_in_adress[1]}\nНа расстоянии: {r_radius} метрах от вас',reply_markup=inline_kb)
        ##debug print(7)
        location_message = await bot.send_location(id, location.latitude, location.longitude)
        ##debug print(8)
        user[f"location_message_id_{id}"] = location_message.message_id
        ##debug print(9)
    except:
        user[f"city_{id}"] = -1
        inline_btn2 = InlineKeyboardButton('Вперёд >>', callback_data='btn_next')
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(inline_btn2)
        await callback_query.message.edit_text('Это был первый ближайший магазин', reply_markup=inline_kb)
        return
    await state.finish()

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_input = message.text
    id = message.from_user.id
    user[f"product_1_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"list_product_{id}"] = worksheet.row_values(worksheet.find("Название сети").row)
    user[f"product_1_{id}"] = [item.lower() for item in user[f"product_1_{id}"]]
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)
    user[f"product_1_{id}"].pop(0)

    user[f"list_product_{id}"].pop(0)
    user[f"list_product_{id}"].pop(0)
    user[f"list_product_{id}"].pop(0)
    keyboard = types.InlineKeyboardMarkup()
    if user_input.lower() in user[f"product_1_{id}"]:
        ind = user[f"product_1_{id}"].index(user_input.lower())
        tovar_ =  user[f"list_product_{id}"][int(ind)]
        #debug print(tovar_)
        callback_data = f'select_product_{tovar_}'  
        keyboard.add(types.InlineKeyboardButton(text=tovar_, callback_data=callback_data))
        await message.reply(f"Информация о товаре {tovar_}: В наличии!\nПодтвердите товар нажав на кнопку.", reply_markup=keyboard)
    if user_input.lower() not in user[f"product_1_{id}"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        button_cancel_product = types.KeyboardButton("Выйти")   
        markup.add(button_cancel_product)
        await message.reply(f"Увы! Ничего не найдено", reply_markup=markup)
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
