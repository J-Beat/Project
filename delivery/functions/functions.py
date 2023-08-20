import configparser as cnf
import json
from datetime import datetime
import time
import requests
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from aiogram import Bot
from typing import Optional, Union, List
import asyncio

from inspect import getsourcefile
from os.path import abspath

# from aiogram.types.


abspath(getsourcefile(lambda:0))



def get_config(group: str, value:str) -> str:
    configPath = 'config/config.ini'
    config = cnf.ConfigParser()  # создаём объекта парсера
    config.read(configPath)
    print(config.sections())
    res = config[group][value]
    return res


def get_texts(name: str) -> dict:
    with open(f"texts/{name}_texts.json", "r") as read_file:
        data = json.load(read_file)
    return data


def get_all_buttons(path: dict) -> list:
    buttons_list = []
    for v in path.values():
        if type(v) == dict:
            val = get_all_buttons(v)
            buttons_list.extend(val)
        elif type(v) == str:
            buttons_list.append(v)
    return buttons_list

def run_to_dict(d:dict) -> dict:
    for k, v in d.items():
        if type(v) == str:
            d[k] = v
        elif type(v) == dict:
            run_to_dict(v)
        else:
            pass
    return d

# def get_link_to_str(string: str) -> str:
#     links = get_texts('links')
#     string = string.format(main = links['main'], price = links['price'], offert = links['offert'], categories = links['categories'], example_1 = links['example_1'], example_2 = links['example_2'], channel = links['channel'], ofd = links["1ofd"])
#     return string


def is_work_time():
    now : datetime = datetime.now()
    if datetime.utcnow().weekday() not in (5, 6):
        if (now.hour > 9) & (now.hour < 20):
            return True
    else:
        return False

async def send_photo(photo:Union[str, list], caption:str, reply_markup:Union[ReplyKeyboardMarkup, InlineKeyboardMarkup], message: Optional[Message] = None, chat_id: Optional[str] = None, bot: Optional[Bot] = None) -> Union[Message, None]:
    if type(photo) == str:
        photo = photo.split('|')
    images: List = []
    for image in photo:
        image = InputMediaPhoto(media=FSInputFile(image))
        images.append(image)
    
    if message != None:
        returned_mediaid = await message.answer_media_group(media=images)
        returned_messageid = await message.answer(text= caption, reply_markup= reply_markup)
    elif (chat_id != None) & (bot != None):
        returned_mediaid = await bot.send_media_group(chat_id= chat_id, media = images)
        returned_messageid = await bot.send_message(chat_id= chat_id, text = caption, reply_markup= reply_markup)
    return returned_mediaid, returned_messageid

    
# Optional[Union[InputFile, str]] = None

async def delete_media(media_ids: str, chat_id: str, bot: Bot):
    media_ids = media_ids.split('|')
    for media_id in media_ids:
        await bot.delete_message(chat_id = chat_id, message_id = int(media_id))


texts = run_to_dict(get_texts('main'))
buttons_list = get_all_buttons(texts['keyboards'])
admin_command = ['/photo_rights', "/block_user", "/help", "/users", "/send_msg", "/send_msg_all"]