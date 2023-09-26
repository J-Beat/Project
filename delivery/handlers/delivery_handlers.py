from aiogram import Router
from aiogram import Bot
from aiogram import types
import aiogram
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
from aiogram import F
from aiogram.filters import StateFilter
from functions.sql_functions import sql_connect as sql_con
# from middlewares.middlewares import PrivateFilterMiddleware
from functions.functions import texts, buttons_list, admin_command, delete_media
from aiogram.filters import Text
import datetime as dt
import sqlite3
import re
import datetime as dt
import logging
import asyncio


ADMIN_CHATID = func.get_config("CHATS_ID", "ADMIN_CHAT")
DELIVERY_CHAT = func.get_config("CHATS_ID", "DELIVERY_CHAT")
WAREHOUSE_CHATID = func.get_config("CHATS_ID", "WAREHOUSE_CHAT")

delivery_router = Router() 


@delivery_router.callback_query(Text("delivery_in_work_button"))
async def change_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    try:
        order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
        data = sql_con.get_order(order_id)
        
        sql_con.modify_order(order_id, 'stage', 'accepted_deliverman')
        sql_con.modify_order(order_id, 'deliveryman_id', callback.from_user.id)
        sql_con.modify_order(order_id, 'deliveryman_name', re.sub('[^ \w\d]', "", callback.from_user.full_name))
        sql_con.modify_order(order_id, 'delivery_group_messageid', callback.message.message_id)
        

        order_message = texts['texts']['order_info'].format(track= data['track_num'], country = data['country'], address = data['address'], password = data['pass'], desc = data['descriprion'], price = data['price'])#message.from_user.full_name
        order_text_to_wh_admin = f"Заказ принят курьером -- {callback.from_user.full_name}\n\n{order_message}"
        order_text_deliver = f"Вы взяли новый заказ. Если вы не заберете заказ в течении 12 часов, он автоматически отменится.\n\n{order_message}"
        
        await func.delete_message(bot, DELIVERY_CHAT, data['delivery_group_messageid'], data['delivery_group_mediaid'])
        await asyncio.sleep(2)
        await func.send_photo(chat_id=callback.from_user.id, sql_con=sql_con, order_id=order_id, chat= 'delivery_private', bot = bot, photo=data['path_image'], caption = order_text_deliver, reply_markup=kb.delivery_private_keyboard)
        try:
            await func.delete_message(bot, ADMIN_CHATID, data['admin_group_messageid'], data['admin_group_mediaid'])
        except Exception as e:
            logging.info(e)
            print(e, order_id)
        await func.send_photo(chat_id=ADMIN_CHATID, sql_con=sql_con, order_id=order_id, chat= 'admin_group', bot = bot, photo=data['path_image'], caption = order_text_to_wh_admin, reply_markup=kb.admin_keyboard)
        await func.delete_message(bot, WAREHOUSE_CHATID, data['warehouse_messageid'], data['warehouse_mediaid'])
        await func.send_photo(chat_id=WAREHOUSE_CHATID, sql_con=sql_con, order_id=order_id, chat= 'warehouse', bot = bot, photo=data['path_image'], caption = order_text_to_wh_admin)

        # if data['admin_group_messageid'] != None:
        #     await bot.edit_message_text(chat_id = ADMIN_CHATID, message_id = int(data['admin_group_messageid']), text= order_text_to_wh_admin, reply_markup=kb.admin_keyboard)
        # else:
        #     await func.send_photo(chat_id=ADMIN_CHATID, bot = bot, photo=data['path_image'], caption = order_text_to_wh_admin, reply_markup=kb.admin_keyboard)
        # if data['warehouse_messageid'] != None:
        #     await bot.edit_message_text(chat_id = WAREHOUSE_CHATID, message_id = int(data['warehouse_messageid']), text= order_text_to_wh_admin)
        # else:
        #     await func.send_photo(chat_id=WAREHOUSE_CHATID, bot = bot, photo=data['path_image'], caption = order_text_to_wh_admin)
        
        await callback.answer()
    except (aiogram.exceptions.TelegramBadRequest, aiogram.exceptions.TelegramForbiddenError) as e:
        logging.info(e)
        print('deliwery in work ERROR ---- ', e)
