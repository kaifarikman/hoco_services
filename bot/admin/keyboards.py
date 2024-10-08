from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from bot.db.schemas.statements import Statements
import bot.db.crud.offices as crud_offices
import bot.db.crud.superusers as crud_superusers

user_menu_buttons = [
    [InlineKeyboardButton(text="Выйти в пользовательское меню", callback_data="start")]
]

user_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=user_menu_buttons)


def go_to_admin_menu_keyboard(user_id):
    menu = "admin"
    if crud_superusers.get_superuser_role(user_id) == 1:
        menu = "superadmin"
    if crud_superusers.get_superuser_role(user_id) == 3:
        menu = "accountant"
    buttons = [[InlineKeyboardButton(text="Выйти в главное меню", callback_data=menu)]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_answer_statement(user_id, statement_id):
    menu = "admin"
    buttons = [
        [
            InlineKeyboardButton(
                text="Продолжить ответ",
                callback_data=f"answer_statement_{statement_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Вернуться к заявке",
                callback_data=f"admin_statement_{statement_id}",
            )
        ],
        [InlineKeyboardButton(text="Выйти в главное меню", callback_data=menu)],
    ]
    if crud_superusers.get_superuser_role(user_id) == 1:
        menu = "superadmin"
        buttons = [
            [
                InlineKeyboardButton(
                    text="Продолжить ответ",
                    callback_data=f"answer_statement_{statement_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Вернуться к заявке",
                    callback_data=f"admin_statement_{statement_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Завершить", callback_data=f"complete_superadmin_{statement_id}"
                ),
            ],
            [InlineKeyboardButton(text="Выйти в главное меню", callback_data=menu)],
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_menu_keyboard(statements: list[Statements], page):
    buttons = []
    static_count = 30
    ind = (page - 1) * static_count
    for _ in range(static_count):
        try:
            statement = statements[ind]
            office_id = statement.office_id
            if office_id is None:
                address = "Адрес требует уточнения"
                if statement.status == 1:
                    text = f"🔵{address}, "
                else:
                    text = f"{address}, "
                if statement.theme is None:
                    text += f"заявка №{statement.id}"
                else:
                    text += f"{statement.theme}"
            else:
                office_id = int(office_id)
                office = crud_offices.read_office(office_id)
                if statement.status == 1:
                    text = f"🔵{office.address}, "
                else:
                    text = f"{office.address}, "
                if statement.theme is None:
                    text += f"офис №{office.office_number}"
                else:
                    text += f"{statement.theme}"
            callback_data = f"admin_statement_{statement.id}"
            button = [InlineKeyboardButton(text=text, callback_data=callback_data)]
            buttons.append(button)
        except Exception as e:
            """рализация indexError , для static_count кнопок без мучений и ифов"""
            pass
        ind += 1

    pages_count = len(statements) // static_count + 1
    if len(statements) % static_count == 0:
        pages_count = len(statements) // static_count

    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(
        text="⬅️", callback_data=f"change_data_{left_page}"
    )
    middle_button = InlineKeyboardButton(
        text=f"{page} из {pages_count}", callback_data="dummy"
    )
    right_button = InlineKeyboardButton(
        text="➡️", callback_data=f"change_data_{right_page}"
    )

    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)

    newsletter = InlineKeyboardButton(
        text="Рассылка", callback_data="send_newsletter_to_user"
    )
    low_menu = [newsletter]
    buttons.append(low_menu)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def statement_keyboard(statement_id, superuser_type):
    if superuser_type in [1, 3]:
        menu = "accountant"
        if superuser_type == 1:
            menu = "superadmin"
        buttons = [
            [
                InlineKeyboardButton(text="Главное меню", callback_data=menu),
                InlineKeyboardButton(
                    text="Тема", callback_data=f"select_statement_theme_{statement_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Завершить",
                    callback_data=f"complete_superadmin_{statement_id}",
                ),
                InlineKeyboardButton(
                    text="В работу", callback_data=f"hire_statement_{statement_id}"
                ),
            ],
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="Главное меню", callback_data="admin"),
                InlineKeyboardButton(
                    text="Тема", callback_data=f"select_statement_theme_{statement_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="В работу", callback_data=f"hire_statement_{statement_id}"
                ),
            ],
        ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="Ответить", callback_data=f"answer_statement_{statement_id}"
            ),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def newsletter_choice(addresses, page, user_id):
    buttons = []
    static_count = 30
    ind = (page - 1) * static_count
    for _ in range(static_count):
        try:
            address = addresses[ind]
            text = f"{address}"
            callback_data = f"send_newsletter_{ind}"
            buttons.append(
                [InlineKeyboardButton(text=text, callback_data=callback_data)]
            )

        except Exception as e:
            """рализация indexError , для static_count кнопок без мучений и ифов"""
            ...
        ind += 1
    pages_count = len(addresses) // static_count
    if len(addresses) % static_count != 0:
        pages_count += 1
    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(
        text="⬅️", callback_data=f"change_newsletter_data_{left_page}"
    )
    middle_button = InlineKeyboardButton(
        text=f"{page} из {pages_count}", callback_data="dummy"
    )
    right_button = InlineKeyboardButton(
        text="➡️", callback_data=f"change_newsletter_data_{right_page}"
    )
    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)
    menu = "admin"
    if crud_superusers.get_superuser_role(user_id) == 1:
        menu = "superadmin"
    if crud_superusers.get_superuser_role(user_id) == 3:
        menu = "accountant"
    menu = [InlineKeyboardButton(text="Выйти в главное меню", callback_data=menu)]
    buttons.append(menu)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def go_to_statement_menu(user_id, statement_id):
    menu = "admin"
    if crud_superusers.get_superuser_role(user_id) == 1:
        menu = "superadmin"
    if crud_superusers.get_superuser_role(user_id) == 3:
        menu = "accountant"
    buttons = [
        [
            InlineKeyboardButton(
                text="Перейти к заявке", callback_data=f"admin_statement_{statement_id}"
            )
        ],
        [InlineKeyboardButton(text="Выйти в главное меню", callback_data=menu)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def user_go_to_statements_keyboard(statement_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Перейти в заявку",
                callback_data=f"my_user_statements_{statement_id}",
            )
        ],
        [InlineKeyboardButton(text="Мои заявки", callback_data="my_statements")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
