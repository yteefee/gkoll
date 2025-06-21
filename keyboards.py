from aiogram.utils.keyboard import ReplyKeyboardBuilder

def base_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Статистика")
    builder.button(text="Помощь")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)