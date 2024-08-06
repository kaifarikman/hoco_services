from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.bot import bot

import bot.db.crud.superusers as crud_superusers
import bot.db.crud.statements as crud_statements
import bot.db.crud.offices as crud_offices
import bot.db.crud.messages as crud_messages
import bot.db.crud.users as crud_users

from bot.db.models.messages import Messages as MessagesModel

import bot.admin.keyboards as keyboards
import bot.admin.texts as texts
import bot.admin.utils as utils

from typing import List
from datetime import datetime


def create_user_message_function(message, album=None):
    lst = []
    if album is None:
        if message.photo:
            media_id = message.photo[-1].file_id
            caption = message.caption
            s = f"photo[]{media_id}[]{caption}"
            lst.append(s)
        elif message.video:
            media_id = message.video.file_id
            caption = message.caption
            s = f"video[]{media_id}[]{caption}"
            lst.append(s)
        elif message.document:
            document_id = message.document.file_id
            caption = message.caption
            s = f"document[]{document_id}[]{caption}"
            lst.append(s)
        elif message.text:
            s = f"text[]None[]{message.text}"
            lst.append(s)
        else:
            return "no format"
    else:
        for element in album:
            if element.photo:
                media_id = element.photo[-1].file_id
                caption = element.caption
                s = f"photo[]{media_id}[]{caption}"
                lst.append(s)
            elif element.video:
                media_id = element.video.file_id
                caption = element.caption
                s = f"video[]{media_id}[]{caption}"
                lst.append(s)
            elif message.document:
                document_id = message.document.file_id
                caption = message.caption
                s = f"document[]{document_id}[]{caption}"
                lst.append(s)
            else:
                return "no format"
        if len(lst) > 3:
            return "to_long"
    return lst


async def send_pretty_statement(user_id, statement_id):
    statement = crud_statements.get_statement_by_id(statement_id)
    superuser_type = crud_superusers.get_superuser_role(user_id)
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
                multi.append([multy_type, file_id])
                if not text:
                    text = "Текст не написан"

        line = f"{user_type}, {date}:\n{text}\n"
        answer += line

    keyboard = keyboards.statement_keyboard(statement_id, superuser_type)
    if len(multi) == 0:
        await bot.send_message(chat_id=user_id, text=answer, reply_markup=keyboard)
    elif len(multi) == 1:
        multimedia_type, file_id = multi[0]
        if multimedia_type == "photo":
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_photo(chat_id=user_id, photo=file_id, reply_markup=keyboard)
        elif multimedia_type == "video":
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_video(chat_id=user_id, video=file_id, reply_markup=keyboard)
        else:
            await bot.send_message(
                chat_id=user_id,
                text=answer,
            )
            await bot.send_document(
                chat_id=user_id, document=file_id, reply_markup=keyboard
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
        await bot.send_media_group(chat_id=user_id, media=media_group)
        await bot.send_message(chat_id=user_id, text=answer, reply_markup=keyboard)


router = Router()


@router.message(Command("admin"))
async def start_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = int(message.from_user.id)
    access_roles = [1, 2]
    access = crud_superusers.get_superuser(user_id, access_roles)

    if access is None or not access:
        return await message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )

    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0
    await message.answer(
        text=texts.access_admin,
        reply_markup=keyboards.admin_menu_keyboard(sort_statements, page),
    )


@router.callback_query(F.data == "admin")
async def start_call_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    access_roles = [1, 2]
    access = crud_superusers.get_superuser(user_id, access_roles)
    if access is None or not access:
        return await callback.message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0
    await callback.message.answer(
        text=texts.access_admin,
        reply_markup=keyboards.admin_menu_keyboard(sort_statements, page),
    )


@router.callback_query(F.data.startswith("change_data_"))
async def change_data_(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    data = str(callback.data).split("_")

    page = int(data[-1])
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    await callback.message.edit_reply_markup(
        reply_markup=keyboards.admin_menu_keyboard(sort_statements, page)
    )


@router.callback_query(F.data == "dummy")
async def dummy_callback(callback: CallbackQuery):
    await callback.answer()


"""check every statement by id"""


@router.callback_query(F.data.startswith("admin_statement_"))
async def admin_statement_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    statement_id = int(callback.data.split("_")[-1])

    user_id = int(callback.from_user.id)

    await send_pretty_statement(user_id, statement_id)


"""start of change statement_theme"""


class StatementTheme(StatesGroup):
    statement_id = State()
    theme = State()


@router.callback_query(F.data.startswith("select_statement_theme_"))
async def select_statement_theme(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    statement_id = int(callback.data.split("_")[-1])
    await callback.message.answer(text=texts.set_theme)
    await state.set_state(StatementTheme.theme)
    await state.update_data({"statement_id": statement_id})


@router.message(StatementTheme.theme)
async def statement_theme(message: Message, state: FSMContext):
    user_id = int(message.from_user.id)
    theme = message.text
    statement_id = int((await state.get_data())["statement_id"])
    crud_statements.update_theme(statement_id, theme)
    await message.answer(
        text=texts.theme_changed,
        reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
    )
    await state.clear()


"""end of change statement_theme"""

"""start statement to work"""


@router.callback_query(F.data.startswith("hire_statement_"))
async def start_statement_(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = int(callback.from_user.id)
    statement_id = int(callback.data.split("_")[-1])
    statement = crud_statements.get_statement_by_id(statement_id)
    if statement.status == 2:
        callback_text = "Заявка уже взята в работу!!!"
        return await callback.answer(text=callback_text)
    await callback.answer()
    await callback.message.edit_reply_markup()
    crud_statements.change_status(statement_id, 2)
    crud_statements.set_date_run(statement_id, datetime.now())

    await callback.message.answer(
        text=texts.status_changed,
        reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
    )


"""end statement to work"""
"""start answer_statement"""


class AnswerStatement(StatesGroup):
    statement_id = State()
    sent_answer = State()


@router.callback_query(F.data.startswith("answer_statement_"))
async def answer_statement_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    statement_id = int(callback.data.split("_")[-1])
    statement = crud_statements.get_statement_by_id(statement_id)
    if statement.status == 1:
        crud_statements.change_status(statement_id, 2)
        crud_statements.set_date_run(statement_id, datetime.now())
    await callback.answer()
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text=texts.sent_answer_to_user,
    )
    await state.set_state(AnswerStatement.sent_answer)
    await state.update_data({"statement_id": statement_id})


@router.message(AnswerStatement.sent_answer)
async def answer_to_user(
    message: Message, state: FSMContext, album: List[Message] = None
):
    statement_id = int((await state.get_data())["statement_id"])
    user_id = int(message.from_user.id)
    await state.clear()

    lst = create_user_message_function(message=message, album=album)
    if lst == "no format":
        return await message.answer(
            text=texts.no_format_to_create_statement,
            reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
        )
    if lst == "to_long":
        return await message.answer(
            text=texts.to_long,
            reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
        )
    data = "{{}}".join(lst)
    multimedia = data
    user_id = int(message.from_user.id)
    type_of_user = "admin"
    now = datetime.now()
    message_db = MessagesModel(
        user_id=user_id,
        type_of_user=type_of_user,
        multimedia=multimedia,
        date=now,
    )

    message_id = crud_messages.create_message(message_db)

    crud_statements.update_messages(statement_id, message_id)

    statement = crud_statements.get_statement_by_id(statement_id)

    user_id = statement.user_id

    await bot.send_message(
        chat_id=user_id,
        text=f"Админ отправил вам ответ по заявке",
        reply_markup=keyboards.user_go_to_statements_keyboard,
    )
    admin_id = int(message.from_user.id)
    await message.answer(
        text=texts.successfully_sent,
        reply_markup=keyboards.go_to_admin_menu_keyboard(admin_id),
    )


"""end answer_statement"""


@router.callback_query(F.data == "send_newsletter_to_user")
async def send_newsletter_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    users = crud_users.get_all_users()
    newsletters = utils.get_newsletters(users)
    user_id = int(callback.from_user.id)

    page = 1 if len(newsletters) != 0 else 0

    await callback.message.answer(
        text=texts.choice_newsletter_text,
        reply_markup=keyboards.newsletter_choice(newsletters, page, user_id),
    )


@router.callback_query(F.data.startswith("change_newsletter_data_"))
async def change_data_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    data = str(callback.data).split("_")
    page = int(data[-1])

    users = crud_users.get_all_users()
    newsletters = utils.get_newsletters(users)
    user_id = int(callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.newsletter_choice(newsletters, page, user_id)
    )


class Newsletter(StatesGroup):
    newsletter_id = State()
    newsletter_text = State()


@router.callback_query(F.data.startswith("send_newsletter_"))
async def send_newsletter_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    """send_newsletter_{office.id}_{user_id}"""
    office_id, user_id = map(int, callback.data.split("_")[-2:])
    address = crud_offices.get_office_address_by_id(office_id)
    await callback.message.answer(
        text=texts.input_newsletter_text(address),
        reply_markup=keyboards.go_to_admin_menu_keyboard(user_id),
    )
    await state.set_state(Newsletter.newsletter_text)
    await state.update_data({"newsletter_id": [office_id, user_id]})


@router.message(Newsletter.newsletter_text)
async def newsletter_text_cmd(message: Message, state: FSMContext):
    data = await state.get_data()
    newsletter_text = message.text
    newsletter_id = data["newsletter_id"]
    chat_id = newsletter_id[1]
    user_id = int(message.from_user.id)
    await bot.send_message(
        chat_id=chat_id,
        text=newsletter_text,
    )
    await message.answer(
        text=texts.newsletter_sent,
        reply_markup=keyboards.go_to_admin_menu_keyboard(user_id),
    )
    await state.clear()
