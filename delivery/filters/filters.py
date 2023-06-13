from aiogram.filters import BaseFilter
from aiogram import Bot, Dispatcher, types
from typing import Union

class NotCommandFilter(BaseFilter):
    def __init__(self, buttons_list: list) -> None:
        self.buttons_list = buttons_list

    async def __call__(self, message: types.Message) -> bool:
        return message.text not in self.buttons_list


class CommandFilter(BaseFilter):
    def __init__(self, buttons_list: list) -> None:
        self.buttons_list = buttons_list

    async def __call__(self, message: types.Message) -> bool:
        return message.text in self.buttons_list


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]) -> None:
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type

class IDFilter(BaseFilter):  # [1]
    def __init__(self, chat_id: Union[str, list]) -> None:
        self.chat_id = chat_id    # [2]

    async def __call__(self, message: types.Message) -> bool:  # [3]
        if isinstance(self.chat_id, str):
            return str(message.chat.id) == self.chat_id
        else:
            return str(message.chat.id) in self.chat_id