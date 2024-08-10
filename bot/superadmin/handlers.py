from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.bot import bot
import config

from bot.db.models.users import Users
from bot.db.models.task_types import TaskTypes
from bot.db.models.offices import Offices
from bot.db.models.meters import Meters
from bot.db.models.superusers import SuperUsers
from bot.db.models.statements import Statements
from bot.db.models.messages import Messages

import bot.db.crud.users as crud_users
import bot.db.crud.task_types as crud_task_types
import bot.db.crud.offices as crud_offices
import bot.db.crud.meters as crud_meters
import bot.db.crud.superusers as crud_superusers
import bot.db.crud.statements as crud_statements
import bot.db.crud.messages as crud_messages

from datetime import datetime
from random import randint

import bot.superadmin.texts as texts
import bot.superadmin.keyboards as keyboards
import bot.superadmin.utils as utils


async def send_to_archive(statement_id):
    """also this is how send_pretty_statement, but to archive"""
    user_id = config.archive_group
    statement = crud_statements.get_statement_by_id(statement_id)
    messages = list(map(int, statement.messages.split()))
    office_id = statement.office_id

    if office_id is None:
        address = "Адрес требует уточнения"
    else:
        address = (
            f"{crud_offices.get_office_address_by_id(office_id)}, офис №{office_id}"
        )

    user = crud_users.read_user(statement.user_id)
    answer = f"{address}\nЗаявка №{statement.id}\nот {user.name}\n+{user.phone}\n"
    multi = list()
    for message_id in messages:
        message = crud_messages.read_message(message_id)
        user_type = "Пользователь"
        if message.type_of_user in ["admin", "superadmin"]:
            user_type = "Админ"
        if message.type_of_user == "accountant":
            user_type = "Бухгалтер"
        date = utils.convert_date(message.date)

        text = ""
        multimedia = message.multimedia.split("{{}}")
        for i in multimedia:
            multy_type, file_id, caption = i.split("[]")
            if multy_type == "text":
                text = caption
            elif multy_type != "text" and caption is not None:
                text = caption
                multi.append([multy_type, file_id])
            elif multy_type != "text" and caption is None:
                multi.append([multy_type, file_id])
                if not text:
                    text = "Текст не написан"
                else:
                    text = multy_type.capitalize()
            else:
                multi.append([multy_type, file_id])
                if not text:
                    text = "Текст не написан"
                else:
                    text = multy_type.capitalize()

        line = f"{user_type}, {date}:\n{text}\n"
        answer += line

    if len(multi) == 0:
        await bot.send_message(
            chat_id=user_id,
            text=answer,
        )
    elif len(multi) == 1:
        multimedia_type, file_id = multi[0]
        if multimedia_type == "photo":
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_photo(
                chat_id=user_id,
                photo=file_id,
            )
        elif multimedia_type == "video":
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_video(
                chat_id=user_id,
                video=file_id,
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_document(
                chat_id=user_id,
                document=file_id,
            )
    else:
        media_group = []
        for element in multi:
            multimedia_type, file_id = element
            if multimedia_type == "photo":
                element_add = InputMediaPhoto(media=file_id, caption=None)
            elif multimedia_type == "video":
                element_add = InputMediaVideo(media=file_id, caption=None)
            else:
                element_add = InputMediaDocument(media=file_id, caption=None)
            media_group.append(element_add)
        await bot.send_message(
            chat_id=user_id,
            text=answer,
        )
        await bot.send_media_group(chat_id=user_id, media=media_group)


router = Router()


@router.message(Command("superadmin"))
async def superadmin_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = int(message.from_user.id)
    if crud_superusers.get_superuser_role(user_id) != 1:
        return await message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )

    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)
    page = 1 if len(sort_statements) != 0 else 0

    await message.answer(
        text=texts.hello_superadmin,
        reply_markup=keyboards.superadmin_keyboard(sort_statements, page),
    )


@router.callback_query(F.data == "superadmin")
async def superadmin_callback_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_superusers.get_superuser_role(user_id) != 1:
        return await callback.message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0

    await callback.message.answer(
        text=texts.hello_superadmin,
        reply_markup=keyboards.superadmin_keyboard(sort_statements, page),
    )


@router.callback_query(F.data.startswith("superadmin_change_data_"))
async def change_data_(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    data = str(callback.data).split("_")

    page = int(data[-1])
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.superadmin_keyboard(sort_statements, page)
    )


@router.callback_query(F.data.startswith("complete_superadmin_"))
async def complete_statement(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    statement_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        text=texts.seriously_complete,
        reply_markup=keyboards.seriously_delete_keyboard(statement_id),
    )


@router.callback_query(F.data == "superadmin_no_complete")
async def superadmin_no_complete(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(
        text=texts.no_complete, reply_markup=keyboards.superadmin_menu_keyboard
    )


@router.callback_query(F.data.startswith("superadmin_complete_"))
async def superadmin_complete_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    statement_id = int(callback.data.split("_")[-1])
    crud_statements.change_status(statement_id, 3)
    crud_statements.set_date_finish(statement_id, datetime.now())
    await send_to_archive(statement_id)
    await callback.message.answer(
        text=texts.sent_to_achieve, reply_markup=keyboards.superadmin_menu_keyboard
    )


@router.callback_query(F.data == "superadmin_newsletter")
async def superadmin_newsletter_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    users = crud_users.get_all_users()
    newsletters = utils.get_newsletters(users)

    page = 1 if len(newsletters) != 0 else 0

    await callback.message.answer(
        text=texts.choice_newsletter_text,
        reply_markup=keyboards.newsletter_choice(newsletters, page),
    )


@router.callback_query(F.data == "superadmin_give_role")
async def superadmin_give_role_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(
        text=texts.give_role, reply_markup=keyboards.give_role
    )


"""начало Функционала ..."""


@router.callback_query(F.data == "give_role_for_superusers")
async def give_role_for_superusers_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    superusers = crud_superusers.get_superusers()
    await callback.message.answer(
        text=texts.select_an_employee_for_settings,
        reply_markup=keyboards.select_an_employee_for_settings(superusers),
    )


@router.callback_query(F.data.startswith("superuser_id_for_select_"))
async def select_id_for_select(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    superuser_id = int(callback.data.split("_")[-1])
    superuser = crud_superusers.read_superuser(superuser_id)
    d = {1: "Группа: суперадмин", 2: "Группа: админ", 3: "Группа: бухгалтер"}
    text = f"Пользователь:\n{superuser.name}\n{d[superuser.superuser_type]}"
    await callback.message.answer(
        text=text, reply_markup=keyboards.select(superuser_id)
    )


class ChangeState(StatesGroup):
    info = State()


@router.callback_query(F.data.startswith("change_to_"))
async def change_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    superuser_type, superuser_id = callback.data.split("_")[-2:]
    name = crud_superusers.read_superuser(int(superuser_id)).name
    await callback.message.answer(
        text=texts.seriously_give_role(superuser_type, name),
        reply_markup=keyboards.go_to_pls,
    )
    await state.set_state(ChangeState.info)
    await state.update_data({"info": [superuser_type, superuser_id]})


@router.callback_query(F.data == "no_to_pls", ChangeState.info)
async def no_to_pls(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(
        text="Успешно отменено", reply_markup=keyboards.superadmin_menu_keyboard
    )


@router.callback_query(F.data == "yes_go_to_pls", ChangeState.info)
async def yes_go_to_pls(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    superuser_type, superuser_id = (await state.get_data())["info"]
    await state.clear()
    d = {
        "superadmin": 1,
        "admin": 2,
        "accountant": 3,
    }
    crud_superusers.update_superuser(int(superuser_id), d[superuser_type])
    await callback.message.answer(
        text="Статус суперпользователя успешно сменен",
        reply_markup=keyboards.superadmin_menu_keyboard,
    )


@router.callback_query(F.data.startswith("delete_person_"))
async def delete_person_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    superuser_id = int(callback.data.split("_")[-1])
    superuser = crud_superusers.read_superuser(superuser_id)

    await callback.message.answer(
        text=texts.really_delete_person(superuser),
        reply_markup=keyboards.really_delete_person(superuser_id),
    )


@router.callback_query(F.data.startswith("delete_really_"))
async def delete_really_person(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    action, superuser_id = callback.data.split("_")[-2:]

    if action == "no":
        return await callback.message.answer(
            text="Успешно отменено", reply_markup=keyboards.superadmin_menu_keyboard
        )
    superuser = crud_superusers.read_superuser(superuser_id)
    crud_superusers.delete_superuser(superuser_id)
    await callback.message.answer(
        text=f"{superuser.name} успешно удален из Базы Данных",
        reply_markup=keyboards.superadmin_menu_keyboard,
    )


class SuperAdminAddNewSuperUser(StatesGroup):
    user_id = State()
    name = State()
    superuser_type_id = State()


@router.callback_query(F.data == "add_new_superuser")
async def add_new_superuser_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(
        text=texts.sent_new_superuser, reply_markup=keyboards.sent_user_id_bot
    )
    await state.set_state(SuperAdminAddNewSuperUser.user_id)


@router.message(SuperAdminAddNewSuperUser.user_id)
async def add_new_superuser_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except Exception:
        return await message.answer(
            text=texts.sent_new_superuser_user_id_please,
            reply_markup=keyboards.superadmin_menu_keyboard,
        )
    await state.update_data({"user_id": user_id})

    await message.answer(text=texts.sent_name)

    await state.set_state(SuperAdminAddNewSuperUser.name)


@router.message(SuperAdminAddNewSuperUser.name)
async def add_new_superuser_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data({"name": name})

    await message.answer(text=texts.sent_superuser_role, reply_markup=keyboards.roles)

    await state.set_state(SuperAdminAddNewSuperUser.superuser_type_id)


@router.callback_query(
    F.data.startswith("set_role_"), SuperAdminAddNewSuperUser.superuser_type_id
)
async def set_role_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    data = await state.get_data()
    await state.clear()

    user_id = int(data["user_id"])
    name = data["name"]
    superuser_type_id = int(callback.data.split("_")[-1])

    superuser = SuperUsers(user_id=user_id, name=name, superuser_type=superuser_type_id)
    crud_superusers.create_superuser(superuser)
    await callback.message.answer(
        text="Сотрудник добавился и получил новые права",
        reply_markup=keyboards.superadmin_menu_keyboard,
    )


@router.callback_query(F.data == "give_role_for_users")
async def give_role_for_users_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(
        text="Выберите действие", reply_markup=keyboards.users_change
    )


class SuperUserDelete(StatesGroup):
    phone_number = State()


@router.callback_query(F.data == "delete_user")
async def delete_user_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(text="Отправьте номер пользователя в формате: 79...")
    await state.set_state(SuperUserDelete.phone_number)


@router.message(SuperUserDelete.phone_number)
async def delete_user_by_phone_number(message: Message, state: FSMContext):
    await state.clear()
    phone_number = str(message.text)
    phone_number = phone_number.replace("+", "")
    id_ = crud_users.get_user_by_phone_number(phone_number)
    if id_ is None:
        return await message.answer(
            text="Пользователя с таким номером в Базе Данных не существует",
            reply_markup=keyboards.superadmin_menu_keyboard,
        )
    crud_users.delete_user(id_)
    await message.answer(
        text="Пользователь удален из Базы Данных",
        reply_markup=keyboards.superadmin_menu_keyboard,
    )


class AddNewUser(StatesGroup):
    name = State()
    inn = State()
    phone_number = State()
    due_date = State()
    address = State()
    office_number = State()
    meters = State()


@router.callback_query(F.data == "add_new_user")
async def add_new_user_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(
        text=texts.add_new_user_name_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.name)


@router.message(AddNewUser.name)
async def add_new_user_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data({"name": name})
    await message.answer(
        text=texts.add_new_user_inn_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.inn)


@router.message(AddNewUser.inn)
async def add_new_user_inn(message: Message, state: FSMContext):
    inn = message.text
    await state.update_data({"inn": inn})
    await message.answer(
        text=texts.add_new_user_phone_number_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.phone_number)


@router.message(AddNewUser.phone_number)
async def add_new_user_phone_number(message: Message, state: FSMContext):
    phone_number = str(message.text)
    phone_number = phone_number.replace("+", "")
    await state.update_data({"phone_number": phone_number})
    await message.answer(
        text=texts.add_new_user_due_date_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.due_date)


@router.message(AddNewUser.due_date)
async def add_new_user_due_date_number(message: Message, state: FSMContext):
    try:
        due_date = int(message.text)
    except Exception as e:

        return await message.answer(
            text="Введите число.", reply_markup=keyboards.superadmin_menu_keyboard
        )
    await state.update_data({"due_date": due_date})
    await message.answer(
        text=texts.add_new_user_office_address_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.address)


@router.message(AddNewUser.address)
async def add_new_user_address_number(message: Message, state: FSMContext):
    address = message.text
    await state.update_data({"address": address})
    await message.answer(
        text=texts.add_new_user_office_office_number_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.office_number)


@router.message(AddNewUser.office_number)
async def add_new_user_office_number_number(message: Message, state: FSMContext):
    office_number = message.text
    await state.update_data({"office_number": office_number})
    await message.answer(
        text=texts.add_new_user_office_meters_text,
        reply_markup=keyboards.superadmin_menu_keyboard,
    )
    await state.set_state(AddNewUser.meters)


@router.message(AddNewUser.meters)
async def add_new_user_due_date(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    name = data["name"]
    inn = data["inn"]
    phone_number = data["phone_number"]
    due_date = int(data["due_date"])
    address = data["address"]
    office_number = data["office_number"]
    meters = message.text

    office_db = Offices(
        address=address,
        office_number=office_number,
        coder_number=None,
        meters=meters
    )
    office_id = crud_offices.create_office(office_db)
    user = Users(
        user_id=None,
        name=name,
        phone=phone_number,
        inn=inn,
        due_date=due_date,
        meter_notification=True,
        rent_notification=True,
        auth=False,
        was_deleted=False,
        statements=None,
        offices=str(office_id),
    )

    crud_users.create_user(user)
    await message.answer(
        text="Пользователь добавлен в Базу Данных",
        reply_markup=keyboards.superadmin_menu_keyboard,
    )


"""конец Функционала ..."""
# заявка завершена? ответ