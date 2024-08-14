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

import bot.accountant.keyboards as keyboards
import bot.accountant.texts as texts
import bot.accountant.utils as utils

from typing import List
from datetime import datetime, timedelta

router = Router()


async def send_pretty_statement(user_id, statement_id):
    info = {
        2: "Подача показаний счетчиков",
        3: "Запрос прочей документации",
        4: "Начисление КУ",
        5: "Начисление аренды",
        6: "Запрос акта сверки",
    }
    statement = crud_statements.get_statement_by_id(statement_id)
    superuser_type = crud_superusers.get_superuser_role(user_id)
    keyboard = keyboards.statement_keyboard(statement_id, superuser_type)
    user = crud_users.read_user(statement.user_id)
    if statement.messages is None:
        address = info[statement.task_type_id]
        answer = f"{address}\nЗаявка №{statement.id}\nот {user.name}\n+{user.phone}"
        return await bot.send_message(
            chat_id=user_id, text=answer, reply_markup=keyboard
        )

    messages = list(map(int, statement.messages.split()))
    office_id = statement.office_id
    office = crud_offices.read_office(office_id)
    if office_id is None:
        address = "Адрес требует уточнения"
    else:
        address = f'{office.address}, офис №{office.office_number}'

    user = crud_users.read_user(statement.user_id)
    answer = f"{address}\nЗаявка №{statement.id}\nот {user.name}\n+{user.phone}\nТема: {statement.theme or 'отсутствует'}\n"
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
            elif multy_type != "text" and caption != "None":
                text = caption
                multi.append([multy_type, file_id])
            elif multy_type != "text" and caption == "None":
                multi.append([multy_type, file_id])
                if not text:
                    text = "-"
            else:
                multi.append([multy_type, file_id])
                if not text:
                    text = "-"

        line = f"{user_type}, {date}\n{text}\n"
        answer += line

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
            else:
                return "no format"
        if len(lst) > 3:
            return "to_long"
    return lst


@router.message(Command("accountant"))
async def start_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = int(message.from_user.id)
    access_roles = [1, 3]
    access = crud_superusers.get_superuser(user_id, access_roles)

    if access is None or not access:
        return await message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )

    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0
    await message.answer(
        text=texts.access_accountant,
        reply_markup=keyboards.accountant_menu_keyboard(sort_statements, page),
    )


@router.callback_query(F.data == "accountant")
async def start_call_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    access_roles = [1, 3]
    access = crud_superusers.get_superuser(user_id, access_roles)
    if access is None or not access:
        return await callback.message.answer(
            text=texts.no_access, reply_markup=keyboards.user_menu_keyboard
        )
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    page = 1 if len(sort_statements) != 0 else 0
    await callback.message.answer(
        text=texts.access_accountant,
        reply_markup=keyboards.accountant_menu_keyboard(sort_statements, page),
    )


@router.callback_query(F.data.startswith("accountant_change_data_"))
async def change_accountant_keyboard(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    data = str(callback.data).split("_")

    page = int(data[-1])
    statements = crud_statements.get_statements()
    sort_statements = utils.sort_statements(statements)

    await callback.message.edit_reply_markup(
        reply_markup=keyboards.accountant_menu_keyboard(sort_statements, page)
    )


@router.callback_query(F.data.startswith("accountant_statement_"))
async def accountant_statement_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    statement_id = int(callback.data.split("_")[-1])

    user_id = int(callback.from_user.id)

    await send_pretty_statement(user_id, statement_id)


"""start of change statement_theme"""


class AccountantStatementTheme(StatesGroup):
    statement_id = State()
    theme = State()


@router.callback_query(F.data.startswith("accountant_select_statement_theme_"))
async def accountant_select_statement_theme_(
        callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup()

    statement_id = int(callback.data.split("_")[-1])
    await callback.message.answer(text=texts.set_theme)
    await state.set_state(AccountantStatementTheme.theme)
    await state.update_data({"statement_id": statement_id})


@router.message(AccountantStatementTheme.theme)
async def accountant_statement_theme(message: Message, state: FSMContext):
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


@router.callback_query(F.data.startswith("accountant_hire_statement_"))
async def accountant_hire_statement_(callback: CallbackQuery, state: FSMContext):
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
    crud_statements.set_date_run(statement_id, datetime.now() + timedelta(hours=3))

    await callback.message.answer(
        text=texts.status_changed,
        reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
    )


"""end statement to work"""
"""start answer_statement"""


class AccountantAnswerStatement(StatesGroup):
    statement_id = State()
    sent_answer = State()


@router.callback_query(F.data.startswith("accountant_answer_statement_"))
async def accountant_answer_statement_callback_(
        callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    statement_id = int(callback.data.split("_")[-1])
    statement = crud_statements.get_statement_by_id(statement_id)
    if statement.status == 1:
        crud_statements.change_status(statement_id, 2)
        crud_statements.set_date_run(statement_id, datetime.now() + timedelta(hours=3))
    await callback.answer()
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text=texts.sent_answer_to_user,
    )
    await state.set_state(AccountantAnswerStatement.sent_answer)
    await state.update_data({"statement_id": statement_id})


@router.message(AccountantAnswerStatement.sent_answer)
async def answer_to_user(
        message: Message, state: FSMContext, album: List[Message] = None
):
    statement_id = int((await state.get_data())["statement_id"])
    user_id = int(message.from_user.id)
    await state.clear()

    info = {
        2: "Подача показаний счетчиков",
        3: "Запрос прочей документации",
        4: "Начисление КУ",
        5: "Начисление аренды",
        6: "Запрос акта сверки",
    }
    if message.voice or message.document:
        return await message.answer(
            text="Запрещено отправлять cообщения данного типа. Отправьте медиа или текстовый ответ",
            reply_markup=keyboards.go_to_statement_menu(user_id, statement_id),
        )
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
    type_of_user = "accountant"
    now = datetime.now() + timedelta(hours=3)
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
        #text=f"Бухгалтер отправил вам ответ на заявку:\n{info[statement.task_type_id]}",
        text=f"Бухгалтер отправил вам ответ на заявку №{statement_id}",
        reply_markup=keyboards.user_go_to_statements_keyboard(statement_id),
    )
    accountant_id = int(message.from_user.id)
    await message.answer(
        text=texts.successfully_sent,
        reply_markup=keyboards.go_to_accountant_menu_keyboard(accountant_id, statement_id),
    )


"""end answer_statement"""
