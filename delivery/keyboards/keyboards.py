from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton

import functions.functions as func
from aiogram import types
texts = func.get_texts('main')


def make_keyboard(path: dict) -> ReplyKeyboardMarkup:
    buttons = []
    values = list(path.values())
    for i in range(0, len(values), 2):
        try:
            buttons.append([types.KeyboardButton(text = values[i]), types.KeyboardButton(text = values[i+1])])
        except IndexError:
            buttons.append([types.KeyboardButton(text = values[i])])

    markup = types.ReplyKeyboardMarkup(keyboard= buttons, resize_keyboard=True)
    return markup

def create_dict_keyboards(keys: dict) -> list:
    res = []
    for k, v in keys.items():
        res.append(make_keyboard(v))
    return res
print()
m = [[types.KeyboardButton(text = texts['keyboards']['manager_main'])]]

main_keybord = types.ReplyKeyboardMarkup(keyboard= m, resize_keyboard=True, one_time_keyboard=True)

# faq_keyboards = create_dict_keyboards(texts['keyboards']['faq'])

# faq_main_keyboards = make_keyboard(texts['keyboards']['faq']['main'])

# faq_registry_keyboard = make_keyboard(texts['keyboards']['faq']['registry'])


# INLINE KEYBOARDS
# manager keyboards
confirm_order = InlineKeyboardButton(text = "Подтвердить заказ", callback_data="confirm_order")
change_order = InlineKeyboardButton(text = "Исправить заказ", callback_data="change_order")
confirm_order_keyboard = InlineKeyboardMarkup(inline_keyboard = [[confirm_order, change_order]], resize_keyboard = True)

track_change = InlineKeyboardButton(text = "Трек номер", callback_data="track_change")
country_change = InlineKeyboardButton(text = "Страна", callback_data="country_change")
address_change = InlineKeyboardButton(text = "Адрес", callback_data="address_change")
pass_change = InlineKeyboardButton(text = "Пароль для получения", callback_data="pass_change")
desc_change = InlineKeyboardButton(text = "Описание заказа", callback_data="desc_change")
price_change = InlineKeyboardButton(text = "Цена доставки", callback_data="price_change")
image_change = InlineKeyboardButton(text = "Изображение с чеком", callback_data="image_change")
back_change = InlineKeyboardButton(text = "Назад", callback_data="back_change")
changee_button_list = [[track_change, country_change], [address_change, pass_change], [desc_change, price_change], [image_change], [back_change]]
change_order_keyboard = InlineKeyboardMarkup(inline_keyboard = changee_button_list, resize_keyboard = True)

one_more_pic = back_change = InlineKeyboardButton(text = "Приложить еще", callback_data="one_more_pic")
fin_pic = back_change = InlineKeyboardButton(text = "Закончить", callback_data="fin_pic")
one_more_keyboard = InlineKeyboardMarkup(inline_keyboard = [[one_more_pic, fin_pic]], resize_keyboard = True)


change_button = InlineKeyboardButton(text = "Изменить", callback_data="just_change")
change_keyboard = InlineKeyboardMarkup(inline_keyboard = [[change_button]], resize_keyboard = True)

wh_in_work = InlineKeyboardButton(text = "Взял в работу", callback_data="wh_in_work")
wh_in_wh = InlineKeyboardButton(text = "Заказ на складе", callback_data="wh_in_wh")
wh_keyboard = InlineKeyboardMarkup(inline_keyboard = [[wh_in_work]], resize_keyboard = True)
wh_keyboard_worked = InlineKeyboardMarkup(inline_keyboard = [[wh_in_wh]], resize_keyboard = True)

delivery_in_work_button = InlineKeyboardButton(text = "Взять в работу", callback_data="delivery_in_work_button")
delivery_group_keyboard = InlineKeyboardMarkup(inline_keyboard = [[delivery_in_work_button]], resize_keyboard = True)


delivery_took_order_button = InlineKeyboardButton(text = "Забрал заказ", callback_data="delivery_took_order_button")
delivery_cant_take_button = InlineKeyboardButton(text = "Не получается забрать заказ", callback_data="delivery_cant_take_button")
delivery_private_keyboard = InlineKeyboardMarkup(inline_keyboard = [[delivery_took_order_button, delivery_cant_take_button]], resize_keyboard = True)

delivery_order_delivered = InlineKeyboardButton(text = "Заказ доставлен", callback_data="delivery_order_delivered")
delivery_delivered_keyboard = InlineKeyboardMarkup(inline_keyboard = [[delivery_order_delivered]], resize_keyboard = True)

admin_close_order_button = InlineKeyboardButton(text = "Закрыть заказ", callback_data="admin_close_order_button")
admin_not_delivered_button = InlineKeyboardButton(text = "Посылка не поступила", callback_data="admin_not_delivered_button")
admin_keyboard = InlineKeyboardMarkup(inline_keyboard = [[admin_close_order_button, admin_not_delivered_button]], resize_keyboard = True)

# price_link_button = InlineKeyboardButton(text = texts['keyboards']['price_subscribe']['price'], url = 'https://xn--80ahhi0afh.xn--p1ai/tariffs??utm_source=Telegram&utm_medium=chatbot&utm_content=tariff&utm_campaign=prodazhi_rf')
# price_link_keyboard = InlineKeyboardMarkup(inline_keyboard = [[price_link_button]], resize_keyboard = True)

# subscribe_link_button = InlineKeyboardButton(text = texts['keyboards']['price_subscribe']['subscribe'], url = 'https://xn--80ahhi0afh.xn--p1ai/tariffs??utm_source=Telegram&utm_medium=chatbot&utm_content=tariff&utm_campaign=prodazhi_rf')
# subscribe_link_keyboard = InlineKeyboardMarkup(inline_keyboard=[[subscribe_link_button]], resize_keyboard = True)


# site_link_button = InlineKeyboardButton(text = '🌐 На сайт', url = 'https://xn--80ahhi0afh.xn--p1ai/?utm_source=Telegram&utm_medium=chatbot&utm_content=main&utm_campaign=prodazhi_rf')
# channel_link_button = InlineKeyboardButton(text = '🔔 В тг-канал', url = 'https://t.me/salesrf')
# site_channek_link_keyboard = InlineKeyboardMarkup(inline_keyboard=[[site_link_button, channel_link_button]], resize_keyboard = True)

# manager_q_button_y = InlineKeyboardButton(text = "Да", callback_data="yes_request_manager")
# manager_q_button_n = InlineKeyboardButton(text = "Нет", callback_data="no_request_manager")
# manager_q_keyboard = InlineKeyboardMarkup(inline_keyboard = [[manager_q_button_y, manager_q_button_n]], resize_keyboard = True)