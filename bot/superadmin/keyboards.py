from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from bot.db.schemas.statements import Statements
import bot.db.crud.offices as crud_offices
import bot.db.crud.superusers as crud_superusers

user_menu_buttons = [
    [InlineKeyboardButton(text="Выйти в главное меню", callback_data="start")]
]
user_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=user_menu_buttons)

superadmin_menu_buttons = [
    [InlineKeyboardButton(text="Выйти в главное меню", callback_data="superadmin")]
]
superadmin_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=superadmin_menu_buttons)


def superadmin_keyboard(statements: list[Statements], page):
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
                address = crud_offices.get_office_address_by_id(office_id)
                if statement.status == 1:
                    text = f"🔵{address}, "
                else:
                    text = f"{address}, "
                if statement.theme is None:
                    text += f"№{office_id}"
                else:
                    text += f"{statement.theme}"

            if statement.task_type_id == 1:
                callback_data = f"admin_statement_{statement.id}"
            else:
                callback_data = f"accountant_statement_{statement.id}"
            button = [InlineKeyboardButton(text=text, callback_data=callback_data)]
            buttons.append(button)
        except Exception as e:
            """рализация indexError , для static_count кнопок без мучений и ифов"""
            ...
        ind += 1
    pages_count = len(statements) // static_count + 1
    if len(statements) % static_count == 0:
        pages_count = len(statements) // static_count
    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(
        text="⬅️", callback_data=f"superadmin_change_data_{left_page}"
    )
    middle_button = InlineKeyboardButton(
        text=f"{page} из {pages_count}", callback_data="dummy"
    )
    right_button = InlineKeyboardButton(
        text="➡️", callback_data=f"superadmin_change_data_{right_page}"
    )

    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)

    newsletter = InlineKeyboardButton(
        text="Рассылка", callback_data="superadmin_newsletter"
    )
    archive = InlineKeyboardButton(text="Архив", url="https://t.me/+EwHO3avMGPZkNTNi")
    give_role = InlineKeyboardButton(text="...", callback_data="superadmin_give_role")
    low_menu = [newsletter, archive, give_role]
    buttons.append(low_menu)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def seriously_delete_keyboard(statement_id):
    buttons = [
        [
            InlineKeyboardButton(text="Нет", callback_data="superadmin_no_complete"),
            InlineKeyboardButton(
                text="Да", callback_data=f"superadmin_complete_{statement_id}"
            ),
        ],
        [InlineKeyboardButton(text="Главное меню", callback_data="superadmin")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def newsletter_choice(newsletters, page):
    buttons = []
    static_count = 30
    ind = (page - 1) * static_count
    for _ in range(static_count):
        try:
            office_id, user_id = newsletters[ind]
            office = crud_offices.read_office(office_id)
            text = f"{office.address}, №{office.office_number}"
            callback_data = f"send_newsletter_{office.id}_{user_id}"
            buttons.append(
                [InlineKeyboardButton(text=text, callback_data=callback_data)]
            )

        except Exception as e:
            """рализация indexError , для static_count кнопок без мучений и ифов"""
            ...
        ind += 1
    pages_count = len(newsletters) // static_count
    if len(newsletters) % static_count != 0:
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
    menu = "superadmin"
    menu = [InlineKeyboardButton(text="Выйти в админ меню", callback_data=menu)]
    buttons.append(menu)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


give_role_buttons = [
    [
        InlineKeyboardButton(
            text="Суперпользователи", callback_data="give_role_for_superusers"
        )
    ],
    [InlineKeyboardButton(text="Пользователи", callback_data="give_role_for_users")],
]

give_role = InlineKeyboardMarkup(inline_keyboard=give_role_buttons)


def select_an_employee_for_settings(superusers):
    buttons = []
    for superuser in superusers:
        text = superuser.name
        callback_data = f"superuser_id_for_select_{superuser.id}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    buttons.append(
        [
            InlineKeyboardButton(
                text="Добавить сотрудника", callback_data="add_new_superuser"
            )
        ]
    )
    buttons.append(
        [InlineKeyboardButton(text="Выйти в меню", callback_data="superadmin")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select(superuser_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Сделать админом", callback_data=f"change_to_admin_{superuser_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Сделать бухгалтером",
                callback_data=f"change_to_accountant_{superuser_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Сделать суперадмином",
                callback_data=f"change_to_superadmin_{superuser_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить сотрудника", callback_data=f"delete_person_{superuser_id}"
            )
        ],
        [InlineKeyboardButton(text="Выйти в меню", callback_data="superadmin")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


go_to_pls_buttons = [
    [
        InlineKeyboardButton(text="Нет", callback_data="no_to_pls"),
        InlineKeyboardButton(text="Да", callback_data="yes_go_to_pls"),
    ],
    [InlineKeyboardButton(text="Главное меню", callback_data="superadmin")],
]

go_to_pls = InlineKeyboardMarkup(inline_keyboard=go_to_pls_buttons)


def really_delete_person(superuser_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Нет", callback_data=f"delete_really_no_{superuser_id}"
            ),
            InlineKeyboardButton(
                text="Да", callback_data=f"delete_really_yes_{superuser_id}"
            ),
        ],
        [InlineKeyboardButton(text="Главное меню", callback_data="superadmin")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


sent_user_id_bot_buttons = [
    [
        InlineKeyboardButton(
            text="Узнать user_id пользователя", url="https://t.me/username_to_id_bot"
        )
    ]
]
sent_user_id_bot = InlineKeyboardMarkup(inline_keyboard=sent_user_id_bot_buttons)

roles_buttons = [
    [InlineKeyboardButton(text="Суперадмин", callback_data="set_role_1")],
    [InlineKeyboardButton(text="Админ", callback_data="set_role_2")],
    [InlineKeyboardButton(text="Бухгалтер", callback_data="set_role_3")],
]
roles = InlineKeyboardMarkup(inline_keyboard=roles_buttons)

users_change_buttons = [
    [InlineKeyboardButton(text="Добавить пользователя", callback_data="add_new_user")],
    [InlineKeyboardButton(text="Удалить пользователя", callback_data="delete_user")],
]

users_change = InlineKeyboardMarkup(inline_keyboard=users_change_buttons)
