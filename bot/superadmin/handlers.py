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
        address = f"{crud_offices.get_office_address_by_id(office_id)}, офис №{office_id}"

    user = crud_users.read_user(statement.user_id)
    answer = f"{address}\nЗаявка №{statement.id}\nот {user.name}\n+{user.phone}\n"
    multi = list()
    for message_id in messages:
        message = crud_messages.read_message(message_id)
        user_type = "Пользователь"
        if message.type_of_user == "admin":
            user_type = "Админ"
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
                multi.append([multy_type, file_id])
                if not text:
                    text = "Текст не написан"

        line = f"{user_type}, {date}:\n{text}\n"
        answer += line

    if len(multi) == 0:
        await bot.send_message(
            chat_id=user_id,
            text=answer,
        )
    if len(multi) == 1:
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
        # TODO: rofllll
        await bot.send_message(
            chat_id=user_id,
            text=answer,
        )
        await bot.send_media_group(
            chat_id=user_id,
            media=media_group
        )


router = Router()


@router.message(Command("change_status"))
async def change_chat(message: Message):
    crud_statements.change_status(1, 2)


@router.message(Command("superadmin"))
async def superadmin_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = int(message.from_user.id)
    if crud_superusers.get_superuser_role(user_id) != 1:
        return await message.answer(
            text=texts.no_access,
            reply_markup=keyboards.user_menu_keyboard
        )
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0

    await message.answer(
        text=texts.hello_superadmin,
        reply_markup=keyboards.superadmin_keyboard(sort_statements, page)
    )


@router.callback_query(F.data == "superadmin")
async def superadmin_callback_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_superusers.get_superuser_role(user_id) != 1:
        return await callback.message.answer(
            text=texts.no_access,
            reply_markup=keyboards.user_menu_keyboard
        )
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0

    await callback.message.answer(
        text=texts.hello_superadmin,
        reply_markup=keyboards.superadmin_keyboard(sort_statements, page)
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
        reply_markup=keyboards.seriously_delete_keyboard(statement_id)
    )


@router.callback_query(F.data == "superadmin_no_complete")
async def superadmin_no_complete(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(
        text=texts.no_complete,
        reply_markup=keyboards.superadmin_menu_keyboard
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
        text=texts.sent_to_achieve,
        reply_markup=keyboards.superadmin_menu_keyboard
    )


@router.callback_query(F.data == "superadmin_newsletter")
async def superadmin_newsletter_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)
    page = 1 if len(sort_statements) != 0 else 0

    await callback.message.answer(
        text=texts.choice_newsletter_text,
        reply_markup=keyboards.newsletter_choice(sort_statements, page)
    )


@router.callback_query(F.data == "superadmin_give_role")
async def superadmin_give_role_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("В доработке")

    # await callback.message.edit_reply_markup()
    # await state.clear()
    #
    # await callback.message.answer(
    #     text=texts.give_role,
    #     reply_markup=keyboards.give_role
    # )


@router.callback_query(F.data == "give_role_for_superusers")
async def give_role_for_superusers_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    superusers = crud_superusers.get_superusers()
    await callback.message.answer(
        text=texts.select_an_employee_for_settings,
        reply_markup=keyboards.select_an_employee_for_settings(superusers)
    )


@router.callback_query(F.data.startswith("superuser_id_for_select_"))
async def select_id_for_select(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    superuser_id = int(callback.data.split("_")[-1])
    superuser = crud_superusers.read_superuser(superuser_id)
    d = {
        1: "Группа: суперадмин",
        2: "Группа: админ",
        3: "Группа: бухгалтер"
    }
    text = f"Пользователь:\n{superuser.name}\nГруппа:\n{d[superuser.superuser_type]}"
    await callback.message.answer(
        text=text,
        reply_markup=keyboards.select(superuser_id)
    )


@router.callback_query(F.data.startswith("change_to_admin_"))
async def change_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    ...

@router.callback_query(F.data == "give_role_for_users")
async def give_role_for_users_callback(callback: CallbackQuery):
    await callback.answer("В доработке")
