import aiogram
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
from states.states import DeliveryStates
import keyboards.keyboards as kb
import functions.functions as func
from aiogram import F
from aiogram.filters import StateFilter
from functions.sql_functions import sql_connect as sql_con
# from middlewares.middlewares import PrivateFilterMiddleware
from functions.functions import texts, buttons_list, admin_command
from aiogram.filters import Text
import datetime as dt
import sqlite3
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pandas as pd
import logging
import asyncio


ADMIN_CHATID = func.get_config("CHATS_ID", "ADMIN_CHAT")
DELIVERY_CHAT = func.get_config("CHATS_ID", "DELIVERY_CHAT")
WAREHOUSE_CHATID = func.get_config("CHATS_ID", "WAREHOUSE_CHAT")
logger = logging.getLogger(__name__)

delivery_private_router = Router() 


@delivery_private_router.callback_query(Text("delivery_took_order_button"))
async def took_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    print("TOOK ORDER")
    await callback.message.delete_reply_markup()
    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    order_message = texts['texts']['order_info'].format(track= data['track_num'], country = data['country'], address = data['address'], password = data['pass'], desc = data['descriprion'], price = data['price'])
    if str(callback.from_user.id) == data['deliveryman_id']:
        # print("TOOK ORDER -- ", data['deliveryman_id'])
        sql_con.modify_order(order_id, 'stage', 'deliveryman_picked_up_order')

        await callback.message.edit_text(text = f"Вы забрали заказ. Нажмите кнопку \"Заказ доставлен\" когда доставите заказ.\n\n{order_message}", reply_markup=kb.delivery_delivered_keyboard)
        try:
            await func.delete_message(bot, ADMIN_CHATID, data['admin_group_messageid'], data['admin_group_mediaid'])
        except Exception as e:
            print(e, order_id)
            logging.info(e)
        await func.send_photo(chat_id=ADMIN_CHATID, sql_con=sql_con, order_id=order_id, chat= 'admin_group', bot = bot, photo=data['path_image'], caption = f"Курьер {callback.from_user.full_name} забрал заказ.\n{order_message}", reply_markup=kb.admin_keyboard)
        # if data['admin_group_messageid'] != None:
        #     await bot.edit_message_text(chat_id = ADMIN_CHATID, message_id = int(data['admin_group_messageid']), text= f"Курьер {callback.from_user.full_name} забрал заказ.\n{order_message}")
        # else:
        #     await func.send_photo(chat_id=ADMIN_CHATID, bot = bot, photo=data['path_image'], caption = f"Курьер {callback.from_user.full_name} забрал заказ.\n"{order_message}, reply_markup=kb.admin_keyboard)
    

    else:
        bot.send_message(callback.from_user.id, text=texts['texts']['delivery']['dont_take'])
    await callback.answer()

    

@delivery_private_router.callback_query(Text("delivery_cant_take_button"))
async def cant_take_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    # print("CANT TOOK ORDER")
    await callback.message.delete_reply_markup()
    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    if str(callback.from_user.id) == data['deliveryman_id']:
        await callback.message.answer(text=texts['texts']['delivery']['cant_take'])
        await state.set_state(DeliveryStates.cant_pickup)
        await state.update_data(cant_pickup=callback.message.text)
        await state.update_data(track_id=order_id)
    else:
        await bot.send_message(callback.from_user.id, text=texts['texts']['delivery']['dont_take'])
    await callback.answer()

@delivery_private_router.callback_query(Text("delivery_order_delivered"))
async def cant_take_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    await callback.message.edit_text(text = callback.message.text.replace("Вы забрали заказ. Нажмите кнопку \"Заказ доставлен\" когда доставите заказ.\n\n", "ЗАКАЗ ДОСТАВЛЕН!\n"))
    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    sql_con.modify_order(order_id, 'stage', 'delivered')
    try:
        await func.delete_message(bot, ADMIN_CHATID, data['admin_group_messageid'], data['admin_group_mediaid'])
    except Exception as e:
        print(e, order_id)
        logging.info(e)
    await func.send_photo(chat_id=ADMIN_CHATID, sql_con=sql_con, order_id=order_id, chat= 'admin_group', bot = bot, photo=data['path_image'], caption = texts['texts']['delivery']['delivered'].format(deliverman = re.sub('[^ \w\d]', "", callback.from_user.full_name), order = re.sub(".+\n\n", "", callback.message.text)), reply_markup=kb.admin_keyboard)

    # if data['admin_group_messageid'] != None:
    #     await bot.edit_message_text(chat_id = ADMIN_CHATID, message_id = int(data['admin_group_messageid']), text= texts['texts']['delivery']['delivered'].format(deliverman = re.sub('[^ \w\d]', "", callback.from_user.full_name), order = order_id))
    # else:
    #     await func.send_photo(chat_id=ADMIN_CHATID, bot = bot, photo=data['path_image'], caption = texts['texts']['delivery']['delivered'].format(deliverman = re.sub('[^ \w\d]', "", callback.from_user.full_name), order = re.sub(".+\n\n", "", callback.message.text)), reply_markup=kb.admin_keyboard)

    
    await callback.answer()
    

@delivery_private_router.message(StateFilter(DeliveryStates.cant_pickup), F.text)
@delivery_private_router.message(StateFilter(DeliveryStates.cant_pickup), F.photo)
async def problem_w_order(message: types.Message, state: FSMContext, sql_con:sql_con, bot:Bot):
    state_data =  await state.get_data()
    order_id = state_data['track_id']
    data = sql_con.get_order(order_id)
    new_message = state_data['cant_pickup'].split('\n\n')[1]
    # print(new_message)
    new_message = f"#order_not_taken\nКурьер {message.from_user.full_name} не смог забрать заказ.\n\nСообщение от курьера -- {message.text}\n\n{new_message}"
    sql_con.modify_order(order_id, 'stage', 'deliveryman_CANT_take_order')
    #   
    try:
        await func.delete_message(bot, ADMIN_CHATID, data['admin_group_messageid'], data['admin_group_mediaid'])
    except Exception as e:
        print(e, order_id)
        logging.info(e)
    await func.send_photo(chat_id=ADMIN_CHATID, sql_con=sql_con, order_id=order_id, chat= 'admin_group', bot = bot, photo=data['path_image'], caption = new_message, reply_markup=kb.admin_keyboard)  
    # if data['admin_group_messageid'] != None:
    #     await bot.edit_message_text(chat_id = ADMIN_CHATID, message_id = int(data['admin_group_messageid']), text= new_message, reply_markup=kb.admin_keyboard)
    # else:
    #     await func.send_photo(chat_id=ADMIN_CHATID, bot = bot, photo=data['path_image'], caption = new_message, reply_markup=kb.admin_keyboard)

    await message.answer(text=texts['texts']['delivery']['send_to_administrators'])
    await state.set_state(DeliveryStates.main)
    


async def checking_reservation_order(sql_con:sql_con, bot:Bot):
    df = sql_con.get_all_orders()
    df = df[df['stage']=='accepted_deliverman']
    if len(df) > 0:
        df['last_change'] = pd.to_datetime(df['last_change'])
        df['current_time'] = dt.datetime.now()
        df['time_delta'] = df['current_time'] - df['last_change']
        df['time_delta'] = df['time_delta'].apply(lambda x: int(x.seconds))
        df = df[df['time_delta'] > 43200]#43200
        records = df.to_dict('records')
        # print('RECORDS ----- ', records)
        for data in records:
            string_to_delivery = texts['texts']['order_info'].format(track= data['track_num'], country = data['country'], address = data['address'], password = data['pass'], desc = data['descriprion'], price = data['price'])#message.from_user.full_name
            image = data['path_image']
            await asyncio.sleep(3)
            try:
                await bot.edit_message_text(chat_id = data['deliveryman_id'], message_id = int(data['delivery_private_messageid']), text= f"{texts['texts']['delivery']['dont_take']}\n\n{string_to_delivery}")
            except TypeError as e:
                logging.info(e)
                try:
                    await func.send_photo(chat_id = data['deliveryman_id'], bot = bot, photo=image, caption = f"{texts['texts']['delivery']['dont_take']}\n\n{string_to_delivery}", reply_markup = None)
                except aiogram.exceptions.TelegramForbiddenError as forbidden:
                    print(data)
                    logging.info(forbidden)
            except aiogram.exceptions.TelegramBadRequest as bad:
                logging.info(f"Order not have delivaryman_id in db. Order id -- {data['track_num']}")
                logging.info(bad)
            except aiogram.exceptions.TelegramForbiddenError as forbidden:
                print(data)
                logging.info(forbidden)
            await func.send_photo(chat_id=DELIVERY_CHAT, sql_con=sql_con, order_id=data['track_num'], chat= 'delivery_group', bot = bot, photo=image, caption = f"НОВЫЙ ЗАКАЗ\n\n{string_to_delivery}\n\n Перед тем как взять заказ неободимо зарегистрироваться в <b><a href='https://t.me/Izhukov_test_bot'>боте</a></b>", reply_markup=kb.delivery_group_keyboard)
            # if data['admin_group_messageid'] != None:
                # await bot.edit_message_text(chat_id = ADMIN_CHATID, message_id = int(data['admin_group_messageid']), text= f"КУРЬЕР НЕ ЗАБРАЛ ЗАКАЗ И ОН ОТПРАВИЛСЯ СНОВА В ГРУППУ КУРЬЕРОВ\n\n{string_to_delivery}", reply_markup=kb.admin_keyboard)
            # else:
            try:
                await func.delete_message(bot, ADMIN_CHATID, data['admin_group_messageid'], data['admin_group_mediaid'])
            except Exception as e:
                print(e, data['track_num'])
                logging.info(e)
            await func.send_photo(chat_id=ADMIN_CHATID, sql_con=sql_con, order_id=data['track_num'], chat= 'admin_group', bot = bot, photo=image, caption = f"КУРЬЕР НЕ ЗАБРАЛ ЗАКАЗ И ОН ОТПРАВИЛСЯ СНОВА В ГРУППУ КУРЬЕРОВ\n\n{string_to_delivery}", reply_markup=kb.admin_keyboard)
            
            # if data['warehouse_messageid'] != None:
                # await bot.edit_message_text(chat_id = WAREHOUSE_CHATID, message_id = int(data['warehouse_messageid']), text= f"КУРЬЕР НЕ ЗАБРАЛ ЗАКАЗ И ОН ОТПРАВИЛСЯ СНОВА В ГРУППУ КУРЬЕРОВ\n\n{string_to_delivery}")
            # else:
            try:
                await func.delete_message(bot, WAREHOUSE_CHATID, data['warehouse_messageid'], data['warehouse_mediaid'])
            except Exception as e:
                print(e, data['track_num'])
                logging.info(e)
            await asyncio.sleep(5)
            await func.send_photo(chat_id=WAREHOUSE_CHATID, sql_con=sql_con, order_id=data['track_num'], chat= 'warehouse', bot = bot, photo=image, caption = f"КУРЬЕР НЕ ЗАБРАЛ ЗАКАЗ И ОН ОТПРАВИЛСЯ СНОВА В ГРУППУ КУРЬЕРОВ\n\n{string_to_delivery}")
            
            sql_con.modify_order(data['track_num'], 'stage', 'in_warehouse')
            sql_con.modify_order(data['track_num'], 'deliveryman_id', '')
            sql_con.modify_order(data['track_num'], 'deliveryman_name', '')
            # sql_con.modify_order(data['track_num'], 'delivery_group_messageid', msg_to_delivery.message_id)
            # sql_con.modify_order(data['track_num'], 'delivery_group_mediaid', '|'.join([str(x.message_id) for x in med_to_delivery]))
