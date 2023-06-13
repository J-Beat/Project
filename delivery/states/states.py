# from aiogram.utils.helper import Helper, HelperMode, ListItem, Item
from aiogram.filters.state import State, StatesGroup


# States
class ManagerStates(StatesGroup):
    main = State()
    country_in = State()
    address_in = State()
    track_in = State()
    pass_in = State()
    desc_in = State()
    price_in = State()
    image_in = State()
    change = State()

class DeliveryStates(StatesGroup):
    main =State()
    cant_pickup = State()


if __name__ == '__main__':
    print(ManagerStates.__all_states__)
