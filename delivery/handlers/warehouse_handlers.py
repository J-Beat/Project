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


ADMIN_CHATID = func.get_config("CHATS_ID", "ADMIN_CHAT")
DELIVERY_CHAT = func.get_config("CHATS_ID", "DELIVERY_CHAT")
WAREHOUSE_CHATID = func.get_config("CHATS_ID", "WAREHOUSE_CHAT")

warehouse_router = Router() 


@warehouse_router.callback_query(Text("wh_in_work"))
async def change_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    await callback.message.edit_text(text = "ЗАКАЗ В РАБОТЕ\n\n" + callback.message.text.replace("Создан новый заказ:\n", ""))
    await callback.message.edit_reply_markup(reply_markup=kb.wh_keyboard_worked)
    warehouser_name = re.sub("\"|\'", "", callback.from_user.full_name)
    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    sql_con.modify_order(order_id, 'stage', 'accepted_warehouse_employee')
    sql_con.modify_order(order_id, 'warehouser_id', callback.from_user.id)
    sql_con.modify_order(order_id, 'warehouser_name', warehouser_name)
    data = sql_con.get_order(order_id)
    await func.send_photo(chat_id= ADMIN_CHATID, bot = bot, photo= data['path_image'], caption= "ЗАКАЗ ПРИНЯТ В РАБОТУ РАБОТНИКОМ СКЛАДА\n\n" + callback.message.text.replace("Создан новый заказ:\n\n", "") + f"\n- Принял в работу -- {warehouser_name}", reply_markup=kb.admin_keyboard)
    await callback.answer()

@warehouse_router.callback_query(Text("wh_in_wh"))
async def change_order(callback: types.CallbackQuery, state: FSMContext, sql_con:sql_con, bot:Bot):
    await callback.message.delete_reply_markup()
    order_id = re.search("- Трек номер -- .+?;", callback.message.text)[0].split(' -- ')[1][:-1]
    data = sql_con.get_order(order_id)
    sql_con.modify_order(order_id, 'stage', 'in_warehouse')
    # await callback.message.id
    await callback.message.edit_text(text = callback.message.text.replace("ЗАКАЗ В РАБОТЕ\n", "ЗАКАЗ НА СКЛАДЕ\n"))
    await func.send_photo(chat_id=ADMIN_CHATID, bot = bot, photo=data['path_image'], caption = callback.message.text.replace("ЗАКАЗ В РАБОТЕ\n", "ЗАКАЗ НА СКЛАДЕ\n"), reply_markup=kb.admin_keyboard)
    messge_to_deivery_chat = await func.send_photo(chat_id=DELIVERY_CHAT, bot = bot, photo=data['path_image'], caption = callback.message.text.replace("ЗАКАЗ В РАБОТЕ\n", "НОВЫЙ ЗАКАЗ\n"), reply_markup=kb.delivery_group_keyboard)
    sql_con.modify_order(order_id, 'delivery_group_messageid', messge_to_deivery_chat.message_id)
    await callback.answer()