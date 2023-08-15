from aiogram import Router
from aiogram import Bot
from aiogram import types
import sys
from pathlib import Path
sys.path.append(str(Path('../delivery').resolve()))
from filters.filters import CommandFilter, NotCommandFilter, ChatTypeFilter, IDFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.message import ContentType
from states.states import ManagerStates
import keyboards.keyboards as kb
import functions.functions as func
from aiogram.types import FSInputFile
from aiogram import F
from aiogram.filters import StateFilter
from functions.sql_functions import sql_connect as sql_con
# from middlewares.middlewares import PrivateFilterMiddleware
from functions.functions import texts, buttons_list, admin_command
from aiogram.filters import Text
import datetime as dt
import sqlite3
import re
from aiogram.types import InputMediaPhoto

ADMIN_CHATID = func.get_config("CHATS_ID", "ADMIN_CHAT")
WAREHOUSE_CHATID = func.get_config("CHATS_ID", "WAREHOUSE_CHAT")


managers_router = Router()  # [1]

@managers_router.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    if message.chat.type == 'private':
        await message.answer(texts['texts']['managers']['greating'], reply_markup=kb.main_keybord, disable_web_page_preview=True)
        print("TYPE USER --- ", type(message.from_user))
        await state.clear()
        await state.set_state(ManagerStates.main)




@managers_router.message(CommandFilter(texts['keyboards'].values()), StateFilter(ManagerStates.main), F.text)
async def create_new_order(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await message.answer(texts['texts']['managers']['track_in'])
    await state.set_state(ManagerStates.track_in)

@managers_router.message(StateFilter(ManagerStates.track_in), F.text)
async def track_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(track_in=re.sub('\W', "", message.text))
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['country_in'])
        await state.set_state(ManagerStates.country_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.country_in), F.text)
async def country_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(country_in=message.text)
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['address_in'])
        await state.set_state(ManagerStates.address_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.address_in), F.text)
async def address_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(address_in=message.text)
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['pass_in'])
        await state.set_state(ManagerStates.pass_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.pass_in), F.text)
async def pass_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(pass_in=message.text)
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['desc_in'])
        await state.set_state(ManagerStates.desc_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.desc_in), F.text)
async def desc_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(desc_in=message.text)
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['price_in'])
        await state.set_state(ManagerStates.price_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.price_in), F.text)
async def price_input(message: types.Message, state: FSMContext, sql_con: sql_con, bot:Bot):
    await state.update_data(price_in=message.text)
    data = await state.get_data()
    if len(data) < 7:
        await message.answer(texts['texts']['managers']['image_in'])
        await state.set_state(ManagerStates.image_in)
    else:
        await confirmation_order(message, state, sql_con, bot)

@managers_router.message(StateFilter(ManagerStates.image_in), F.photo)
async def impage_in(message: types.Message, state: FSMContext, sql_con: sql_con, bot: Bot):
    data = await state.get_data()
    track_id = data['track_in']
    image_path = f'images/{track_id}_image_{str(dt.datetime.now())}.jpg'
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, image_path)
    print(data, type(data))

    if 'image_in' in data.keys():
        print(data['image_in'])
        path = data['image_in'] + [image_path]
        await state.update_data(image_in=path)
    else:
        await state.update_data(image_in=[image_path])
    await message.answer(text=texts['texts']['managers']['some_pic'], reply_markup=kb.one_more_keyboard)

@managers_router.callback_query(Text("one_more_pic"))
async def one_more_pic(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(texts['texts']['managers']['image_in'])
    await state.set_state(ManagerStates.image_in)
    await callback.answer()

@managers_router.callback_query(Text("fin_pic"))
async def fin_pic(callback: types.CallbackQuery, bot:Bot, state: FSMContext, sql_con: sql_con):
    await callback.message.delete_reply_markup()
    await confirmation_order(callback, state, sql_con, bot)
    await callback.answer()

@managers_router.callback_query(Text("confirm_order"))
async def confirm_new_order(callback: types.CallbackQuery, bot:Bot, state: FSMContext, sql_con: sql_con):#
    await callback.message.delete_reply_markup()
    await callback.answer()
    
    data = await state.get_data()
    track_id = data['track_in']
    country = data['country_in']
    address = data['address_in']
    password = data['pass_in']
    desc = data['desc_in']
    price = data['price_in']
    image_path = data['image_in']
    try:
        sql_con.add_new_order(data=(track_id, country, address, password, desc, price, "|".join(image_path), "created", str(dt.datetime.now()), callback.from_user.id, re.sub("\"|\'", "", callback.from_user.full_name)))
        await callback.message.answer(texts['texts']['managers']['created'], reply_markup= kb.main_keybord)

        string_to_warehouse = texts['texts']['warehouse']['new_order'].format(track= track_id, country = country, address = address, password = password, desc = desc, price = price, manager = callback.from_user.full_name)#message.from_user.full_name
        string_to_admin = texts['texts']['administrators']['new_order'].format(track= track_id, country = country, address = address, password = password, desc = desc, price = price, manager = callback.from_user.full_name)#message.from_user.full_name
        msg_to_wh = await func.send_photo(chat_id= WAREHOUSE_CHATID, bot=bot, photo= image_path, caption= string_to_warehouse, reply_markup= kb.wh_keyboard)
        sql_con.modify_order(track_id, 'warehouse_messageid', msg_to_wh.message_id)
        await func.send_photo(chat_id= ADMIN_CHATID, bot = bot, photo= image_path, caption= string_to_admin, reply_markup=kb.admin_keyboard)
        await state.clear()
        await state.set_state(ManagerStates.main)

    except(sqlite3.IntegrityError):
        await callback.message.answer(texts['texts']['managers']['double_track'].format(track_id= track_id), reply_markup=kb.change_keyboard)
    await callback.answer()



@managers_router.callback_query(Text("change_order"))
async def change_order(callback: types.CallbackQuery, state: FSMContext):
    
    await callback.message.delete_reply_markup()
    await callback.message.answer(texts['texts']['managers']['change'], reply_markup=kb.change_order_keyboard)
    # print(await state.get_state(), await state.get_data())
    await state.set_state(ManagerStates.change)
    await callback.answer()

@managers_router.callback_query(Text("track_change"), StateFilter(ManagerStates.change))#
async def change_track(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.track_in)
    await callback.message.answer(texts['texts']['managers']['track_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("just_change"))
async def change_double_track(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.track_in)
    await callback.message.answer(texts['texts']['managers']['track_in'])
    await callback.answer()

@managers_router.callback_query(Text("country_change"), StateFilter(ManagerStates.change))
async def change_country(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.country_in)
    await callback.message.answer(texts['texts']['managers']['country_in'])
    await callback.answer()
    
@managers_router.callback_query(Text("address_change"), StateFilter(ManagerStates.change))
async def change_address(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.address_in)
    await callback.message.answer(texts['texts']['managers']['address_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("pass_change"), StateFilter(ManagerStates.change))
async def change_pass(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.pass_in)
    await callback.message.answer(texts['texts']['managers']['pass_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("desc_change"), StateFilter(ManagerStates.change))
async def change_desc(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.desc_in)
    await callback.message.answer(texts['texts']['managers']['desc_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("price_change"), StateFilter(ManagerStates.change))
async def change_price(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.price_in)
    await callback.message.answer(texts['texts']['managers']['price_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("image_change"), StateFilter(ManagerStates.change))
async def change_image(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ManagerStates.image_in)
    await callback.message.answer(texts['texts']['managers']['image_in'])
    await callback.answer()
    

@managers_router.callback_query(Text("back_change"), StateFilter(ManagerStates.change))
async def send_random_value(callback: types.CallbackQuery, state: FSMContext, bot:Bot):
    await callback.message.edit_reply_markup(reply_markup=kb.confirm_order_keyboard)
    await callback.answer()

#

async def confirmation_order(message: types.CallbackQuery, state: FSMContext, sql_con: sql_con, bot: Bot):
    data = await state.get_data()
    track_id = data['track_in']
    country = data['country_in']
    address = data['address_in']
    password = data['pass_in']
    desc = data['desc_in']
    price = data['price_in']
    image_path = data['image_in']
    print("IMAGE_PATH -------- ", image_path)

    string_to_answer = texts['texts']['managers']['summary'].format(track= track_id, country = country, address = address, password = password, desc = desc, price = price)
    await func.send_photo(chat_id=message.from_user.id, bot = bot, photo= image_path, caption=string_to_answer, reply_markup=kb.confirm_order_keyboard)
    await state.set_state(ManagerStates.main)