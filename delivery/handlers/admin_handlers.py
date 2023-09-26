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
from functions.functions import texts, buttons_list, admin_command, delete_media
from aiogram.filters import Text
import datetime as dt
import sqlite3
import re
import aiogram
import logging


ADMIN_CHATID = func.get_config("CHATS_ID", "ADMIN_CHAT")
DELIVERY_CHAT = func.get_config("CHATS_ID", "DELIVERY_CHAT")
WAREHOUSE_CHATID = func.get_config("CHATS_ID", "WAREHOUSE_CHAT")

admin_router = Router() 


@admin_router.callback_query(Text("admin_close_order_button"))
async def close_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):

    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    sql_con.modify_order(order_id, 'stage', 'closed')
    order_message = texts['texts']['order_info'].format(track= data['track_num'], country = data['country'], address = data['address'], password = data['pass'], desc = data['descriprion'], price = data['price'])
    new_message = f"ЗАКАЗ ЗАКРЫТ\n{order_message}"

    if data != None:
        if data['delivery_group_messageid'] != None:
            try:
                # await bot.delete_message(chat_id = DELIVERY_CHAT, message_id = int(data['delivery_group_messageid']))
                # await delete_media(data['delivery_group_mediaid'], DELIVERY_CHAT, bot)
                await func.delete_message(bot, DELIVERY_CHAT, data['delivery_group_messageid'], data['delivery_group_mediaid'])
            except aiogram.exceptions.TelegramBadRequest as e:
                print(e, '--------', order_id)
                logging.info(f"{e} -- {order_id}")

        if data['delivery_private_messageid'] != None:
            if data['deliveryman_id'] != '':
                try:
                    # await bot.delete_message(chat_id = data['deliveryman_id'], message_id = int(data['delivery_private_messageid']))
                    # await delete_media(data['delivery_private_mediaid'], data['deliveryman_id'], bot)
                    await func.delete_message(bot, data['deliveryman_id'], data['delivery_private_messageid'], data['delivery_private_mediaid'])
                except aiogram.exceptions.TelegramBadRequest as e:
                    print(e, '--------', order_id)
                    logging.info(f"{e} -- {order_id}")
        if data['warehouse_messageid'] != None:
            try:
                # await bot.delete_message(chat_id = WAREHOUSE_CHATID, message_id = int(data['warehouse_messageid']))
                # await delete_media(data['warehouse_mediaid'], WAREHOUSE_CHATID, bot)
                await func.delete_message(bot, WAREHOUSE_CHATID, data['warehouse_messageid'], data['warehouse_mediaid'])
            except aiogram.exceptions.TelegramBadRequest as e:
                print(e, '--------', order_id)
                logging.info(f"{e} -- {order_id}")

        await callback.message.edit_text(text=new_message)
        await callback.answer()
    else:
        print("DATA NONE FOR ORDER ----- ", order_id)


@admin_router.callback_query(Text("admin_not_delivered_button"))
async def order_not_delivered(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):

    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    sql_con.modify_order(order_id, 'stage', 'closed')
    
    order_message = texts['texts']['order_info'].format(track= data['track_num'], country = data['country'], address = data['address'], password = data['pass'], desc = data['descriprion'], price = data['price'])
    new_message_to_all = f"ЗАКАЗ ЗАКРЫТ\n{order_message}"
    new_message_to_admin = f"#not_delivered\nПосылка не поступила\n{order_message}"

    if data != None:
        if data['delivery_group_messageid'] != None:
            try:
                # await bot.delete_message(chat_id = DELIVERY_CHAT, message_id = int(data['delivery_group_messageid']))
                # await delete_media(data['delivery_group_mediaid'], DELIVERY_CHAT, bot)
                await func.delete_message(bot, DELIVERY_CHAT, data['delivery_group_messageid'], data['delivery_group_mediaid'])
            except aiogram.exceptions.TelegramBadRequest as e:
                print(e, '--------', order_id)
                logging.info(f"{e} -- {order_id}")

        if data['delivery_private_messageid'] != None:
            if data['deliveryman_id'] != '':
                try:
                    # await bot.delete_message(chat_id = data['deliveryman_id'], message_id = int(data['delivery_private_messageid']))
                    # await delete_media(data['delivery_private_mediaid'], data['deliveryman_id'], bot)
                    await func.delete_message(bot, data['deliveryman_id'], data['delivery_private_messageid'], data['delivery_private_mediaid'])
                except aiogram.exceptions.TelegramBadRequest as e:
                    print(e, '--------', order_id)
                    logging.info(f"{e} -- {order_id}")
        if data['warehouse_messageid'] != None:
            try:
                # await bot.delete_message(chat_id = WAREHOUSE_CHATID, message_id = int(data['warehouse_messageid']))
                # await delete_media(data['warehouse_mediaid'], WAREHOUSE_CHATID, bot)
                await func.delete_message(bot, WAREHOUSE_CHATID, data['warehouse_messageid'], data['warehouse_mediaid'])
            except aiogram.exceptions.TelegramBadRequest as e:
                print(e, '--------', order_id)
                logging.info(f"{e} -- {order_id}")
    else:
        print(f'NOT DATA FOR ORDER ----- {order_id}')

    await callback.message.edit_text(text=new_message_to_admin)
    await callback.answer()
