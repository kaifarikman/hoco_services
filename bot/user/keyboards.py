from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from bot.db.schemas.statements import Statements

import bot.db.crud.offices as crud_offices
import bot.db.crud.statements as crud_statements


def user_statements_keyboard(user_statements: list[Statements], page):
    buttons = []
    ind = (page - 1) * 30
    for _ in range(30):
        try:
            statement = user_statements[ind]
            office_id = statement.office_id
            if office_id is None:
                address = "Адрес требует уточнения"
            else:
                address = crud_offices.get_office_address_by_id(office_id)

            text = ""
            if statement.status == 3:
                text += "✅"
            text += address + ", "
            if statement.theme is None:
                text += f"№{office_id}"
            else:
                text += f"{statement.theme}"
            callback_data = f"my_user_statements_{statement.id}"
            button = [InlineKeyboardButton(text=text, callback_data=callback_data)]
            buttons.append(button)
        except Exception as e:
            """рализация indexError , для 8 кнопок без мучений и ифов"""
            ...
        ind += 1
    pages_count = (
        len(user_statements) // 8 + 1
        if len(user_statements) % 8 != 0
        else len(user_statements) // 8
    )
    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(
        text="⬅️", callback_data=f"user_statements_keyboard_data_{left_page}"
    )
    middle_button = InlineKeyboardButton(
        text=f"{page} из {pages_count}", callback_data="dummy"
    )
    right_button = InlineKeyboardButton(
        text="➡️", callback_data=f"user_statements_keyboard_data_{right_page}"
    )

    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)
    buttons.append(
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_counter(meters, office_id):
    buttons = []
    for meter in meters:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{meter[0]}",
                    callback_data=f"meter_callback_{meter[1]}_{office_id}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_high_counter(meters, office_id):
    buttons = []
    for meter in meters:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{meter[0]}",
                    callback_data=f"high_meter_callback_{meter[1]}_{office_id}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_offices(offices):
    buttons = []
    for office in offices:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{office[0]}, оф. №{office[1]}",
                    callback_data=f"office_callback_{office[2]}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_user_statement_keyboard(statement_id):
    statement = crud_statements.get_statement_by_id(statement_id)

    buttons = [
        [
            InlineKeyboardButton(text="Главное меню", callback_data="start"),
        ],
        [
            InlineKeyboardButton(
                text="Вернуться к заявкам", callback_data=f"my_statements"
            )
        ],
    ]
    if statement.status != 3:
        buttons[0].append(
            InlineKeyboardButton(
                text="Ответить", callback_data=f"sent_answer_{statement_id}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


start_true_buttons = [
    [InlineKeyboardButton(text="Мои заявки", callback_data="my_statements")],
    [InlineKeyboardButton(text="Новая заявка", callback_data="new_statement")],
    [
        InlineKeyboardButton(
            text="Подача показаний счетчика", callback_data="submitting_meter_readings"
        )
    ],
    [
        InlineKeyboardButton(
            text="Запрос прочей документации",
            callback_data="request_for_other_documentation",
        )
    ],
    [InlineKeyboardButton(text="Начисление КУ", callback_data="ku_accuracy")],
    [InlineKeyboardButton(text="Начисление аренды", callback_data="rent_accuracy")],
    [
        InlineKeyboardButton(
            text="Запрос акта сверки", callback_data="request_for_reconciliation_report"
        )
    ],
]

start_true_keyboard = InlineKeyboardMarkup(inline_keyboard=start_true_buttons)

start_false_buttons = [
    [InlineKeyboardButton(text="Получить доступ", callback_data="gain_access")]
]

start_false_keyboard = InlineKeyboardMarkup(inline_keyboard=start_false_buttons)

back_buttons = [
    [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
]

back_keyboard = InlineKeyboardMarkup(inline_keyboard=back_buttons)

first_button = KeyboardButton(
    text="Отправить номер телефона",
    request_contact=True,
)
send_number_keyboard = ReplyKeyboardMarkup(
    keyboard=[[first_button]], resize_keyboard=True, one_time_keyboard=True
)

remove_reply_markup = ReplyKeyboardRemove()

go_to_send_statement_buttons = [
    [InlineKeyboardButton(text="Да", callback_data="send_it")],
    [InlineKeyboardButton(text="Нет", callback_data="no_send_it")],
]
go_to_send_statement_keyboard = InlineKeyboardMarkup(
    inline_keyboard=go_to_send_statement_buttons
)

go_to_send_statement_middle_buttons = [
    [InlineKeyboardButton(text="Да", callback_data="send_it_middle")],
    [InlineKeyboardButton(text="Нет", callback_data="no_send_it_middle")],
]

go_to_send_statement_keyboard_middle = InlineKeyboardMarkup(
    inline_keyboard=go_to_send_statement_middle_buttons
)

go_to_send_statement_high_buttons = [
    [InlineKeyboardButton(text="Да", callback_data="send_it_high")],
    [InlineKeyboardButton(text="Нет", callback_data="no_send_it_high")],
]

go_to_send_statement_keyboard_high = InlineKeyboardMarkup(
    inline_keyboard=go_to_send_statement_high_buttons
)
