from aiogram.fsm.state import StatesGroup, State


class CheckoutStates(StatesGroup):
    waiting_discount = State()
    waiting_address = State()
    waiting_note = State()
    waiting_delivery_method = State()
    waiting_coin_choice = State()
