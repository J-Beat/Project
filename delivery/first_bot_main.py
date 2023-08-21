import configparser as cnf
import asyncio
from typing import Text
import sys
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, Dispatcher, types#executor, 
# from aiogram.dispatcher import filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.message import ContentType
# import keyboards as kb
import functions.functions as func
# from bot_filters import CommandFilter, NotCommandFilter, ChatTypeFilter, IDFilter
# from states.main_states import MainStates, FaqStates, AdminStates 
from aiogram.fsm.storage.memory import MemoryStorage
from functions.sql_functions import sql_connect as sql
import logging
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage
import middlewares.middlewares as md
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.managers_handlers import managers_router
from handlers.warehouse_handlers import warehouse_router
from handlers.delivery_handlers import delivery_router
from handlers.delivery_private_handlers import delivery_private_router, checking_reservation_order
from handlers.admin_handlers import admin_router


async def start_bot():
    file_handler = logging.FileHandler(filename="logger.log", mode="a")
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level = logging.INFO, format = "%(asctime)s - [%(levelname)s]) - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", handlers=[stdout_handler, file_handler])
    logger = logging.getLogger(__name__)
    sql_con = sql('orders', logger)
    # sql_con.create_users_table()
    token = func.get_config("TOKEN", "MAIN_TOKEN")
    bot = Bot(token = token, parse_mode="HTML")
    storage = RedisStorage.from_url('redis://localhost:6379/0')

    
    dp = Dispatcher(storage=storage)
    
    dp.update.outer_middleware.register(md.MainMiddleware(sql_con))
    # dp.message.outer_middleware.register(md.CallbackMiddleware(sql_con))
    dp.include_router(managers_router)
    dp.include_router(warehouse_router)
    dp.include_router(delivery_router)
    dp.include_router(delivery_private_router)
    dp.include_router(admin_router)
    # main_router.message.middleware(md.PrivateFilterMiddleware(sql_con))
    # dp.include_router(main_router)
    # admin_router.message.middleware(md.GroupFilterMiddleware(sql_con))
    # dp.include_router(admin_router)
    # chat_router.message.middleware(md.UserPermissionMiddleware(sql_con)) 
    # dp.include_router(chat_router)


    scheduler = AsyncIOScheduler()
    scheduler.add_job(checking_reservation_order, "interval", seconds=1800, args=(sql_con, bot))
    scheduler.start()
    
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())