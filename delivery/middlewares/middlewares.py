from datetime import datetime
from typing import Callable, Dict, Any, Awaitable
import sys
from pathlib import Path
sys.path.append(str(Path('../delivery').resolve()))
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.types import TelegramObject
# from functions.sql_functions import sql_connect as sql
from functions.functions import is_work_time, texts
from functions.sql_functions import sql_connect as sql_con
from datetime import datetime
import asyncio
from typing import List, Union

# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.dispatcher.event import handler#.handler import CancelHandler
# from aiogram.dispatcher.middlewares import BaseMiddleware


class MainMiddleware(BaseMiddleware):
    def __init__(self, sqlcon):
        self.sqlcon = sqlcon

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['sql_con'] = self.sqlcon
        # print(event)
        # self.sqlcon.modify_user_info(user = str(event.from_user.id), col = "lastComm", val = str(datetime.now()))
        # self.sqlcon.write_update(user = str(event.from_user.id), message = str(event.text))
        return await handler(event, data)
        # В противном случае просто вернётся None
        # и обработка прекратится





# class AlbumMiddleware(BaseMiddleware):
#     """This middleware is for capturing media groups."""

#     album_data: dict = {}

#     def __init__(self, latency: Union[int, float] = 0.01):
#         """
#         You can provide custom latency to make sure
#         albums are handled properly in highload.
#         """
#         self.latency = latency
#         super().__init__()

#     async def on_process_message(self, message: types.Message, data: dict):
#         if not message.media_group_id:
#             return

#         try:
#             self.album_data[message.media_group_id].append(message)
            
#             raise CancelHandler()  # Tell aiogram to cancel handler for this group element
#         except KeyError:
#             self.album_data[message.media_group_id] = [message]
#             await asyncio.sleep(self.latency)

#             message.conf["is_last"] = True
#             data["album"] = self.album_data[message.media_group_id]

#     async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
#         """Clean up after handling our album."""
#         if message.media_group_id and message.conf.get("is_last"):
#             del self.album_data[message.media_group_id]