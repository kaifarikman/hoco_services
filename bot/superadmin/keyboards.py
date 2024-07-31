from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from bot.db.schemas.statements import Statements
import bot.db.crud.offices as crud_offices

user_menu_buttons = [
    [
        InlineKeyboardButton(text="Выйти в главное меню", callback_data="start")
    ]
]
user_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=user_menu_buttons)

superadmin_menu_buttons = [
    [
        InlineKeyboardButton(text="Выйти в главное меню", callback_data="superadmin")
    ]
]
superadmin_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=superadmin_menu_buttons)


def superadmin_keyboard(statements: list[Statements], page):
    buttons = []
    ind = (page - 1) * 8
    for _ in range(8):

        try:
            statement = statements[ind]
            office_id = statement.office_id
            if office_id is None:
                address = "Адрес требует уточнения"
                if statement.status != 1:
                    text = f"{address}, "
                else:
                    text = f"🔵{address}, "
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
            '''рализация indexError , для 8 кнопок без мучений и ифов'''
            ...
        ind += 1
    pages_count = len(statements) // 8 + 1 if len(statements) % 8 != 0 else len(statements) // 8
    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(text="⬅️", callback_data=f"superadmin_change_data_{left_page}")
    middle_button = InlineKeyboardButton(text=f"{page} из {pages_count}", callback_data="dummy")
    right_button = InlineKeyboardButton(text="➡️", callback_data=f"superadmin_change_data_{right_page}")

    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)

    newsletter = InlineKeyboardButton(text="Рассылка", callback_data="superadmin_newsletter")
    archive = InlineKeyboardButton(text="Архив", url="https://t.me/+EwHO3avMGPZkNTNi")
    give_role = InlineKeyboardButton(text="...", callback_data="superadmin_give_role")
    low_menu = [newsletter, archive, give_role]
    buttons.append(low_menu)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def seriously_delete_keyboard(statement_id):
    buttons = [
        [
            InlineKeyboardButton(text="Нет", callback_data="superadmin_no_complete"),
            InlineKeyboardButton(text="Да", callback_data=f"superadmin_complete_{statement_id}")
        ],
        [
            InlineKeyboardButton(text="Главное меню", callback_data="superadmin")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def newsletter_choice(statements, page):
    buttons = []
    ind = (page - 1) * 8
    for _ in range(8):
        try:
            statement = statements[ind]
            office_id = int(statement.office_id)
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
                callback_data = f"admin_newsletter_{statement.id}"
            else:
                callback_data = f"accountant_newsletter_{statement.id}"
            button = [InlineKeyboardButton(text=text, callback_data=callback_data)]
            buttons.append(button)
        except Exception as e:
            '''рализация indexError , для 8 кнопок без мучений и ифов'''
            ...
        ind += 1
    pages_count = len(statements) // 8 + 1 if len(statements) % 8 != 0 else len(statements) // 8
    left_page = page - 1 if page != 1 else pages_count
    right_page = page + 1 if page != pages_count else 1
    left_button = InlineKeyboardButton(text="⬅️", callback_data=f"change_newsletter_data_{left_page}")
    middle_button = InlineKeyboardButton(text=f"{page} из {pages_count}", callback_data="dummy")
    right_button = InlineKeyboardButton(text="➡️", callback_data=f"change_newsletter_data_{right_page}")
    configuration_field = [left_button, middle_button, right_button]
    buttons.append(configuration_field)
    menu = [InlineKeyboardButton(text="Выйти в меню", callback_data="superadmin")]
    buttons.append(menu)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


give_role_buttons = [
    [
        InlineKeyboardButton(text="Суперпользователи", callback_data="give_role_for_superusers")
    ],
    [
        InlineKeyboardButton(text="Пользователи", callback_data="give_role_for_users")
    ],
]

give_role = InlineKeyboardMarkup(inline_keyboard=give_role_buttons)


def select_an_employee_for_settings(superusers):
    buttons = []
    for superuser in superusers:
        text = superuser.name
        callback_data = f"superuser_id_for_select_{superuser.id}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    buttons.append([InlineKeyboardButton(text="Добавить сотрудника", callback_data="add_new_superuser")])
    buttons.append([InlineKeyboardButton(text="Выйти в меню", callback_data="superadmin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select(superuser_id):
    buttons = [[
        InlineKeyboardButton(text="Сделать админом", callback_data=f"change_to_admin_{superuser_id}")
    ], [
        InlineKeyboardButton(text="Сделать бухгалтером", callback_data=f"change_to_accountant_{superuser_id}")
    ], [
        InlineKeyboardButton(text="Сделать супеадмином", callback_data=f"change_to_superadmin_{superuser_id}")
    ], [
        InlineKeyboardButton(text="Удалить сотрудника", callback_data=f"delete_person_{superuser_id}")
    ], [InlineKeyboardButton(text="Выйти в меню", callback_data="superadmin")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


go_to_pls_buttons = [
    [
        InlineKeyboardButton(text="Нет", callback_data="no_to_pls"),
        InlineKeyboardButton(text="ДА", callback_data="yes_go_to_pls")
    ],
    [
        InlineKeyboardButton(text="Главное меню", callback_data="superadmin")
    ]
]

go_to_pls = InlineKeyboardMarkup(inline_keyboard=go_to_pls_buttons)
