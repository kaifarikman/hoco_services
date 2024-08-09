from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from typing import List

import bot.user.texts as texts
import bot.user.keyboards as keyboards
import bot.user.utils as utils

from bot.db.models.messages import Messages as MessagesModel
from bot.db.models.statements import Statements as StatementsModel
from bot.db.models.users import Users as UsersModel

import bot.db.crud.users as crud_users
import bot.db.crud.messages as crud_messages
import bot.db.crud.statements as crud_statements
import bot.db.crud.offices as crud_offices
import bot.db.crud.meters as crud_meters
import bot.db.crud.superusers as crud_superusers

from bot.bot import bot
from datetime import datetime

"""start help functions"""


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
    info = {
        2: "Подача показаний счетчиков",
        3: "Запрос прочей документации",
        4: "Начисление КУ",
        5: "Начисление аренды",
        6: "Запрос акта сверки",
    }
    statement = crud_statements.get_statement_by_id(statement_id)
    user = crud_users.read_user(statement.user_id)
    keyboard = keyboards.create_user_statement_keyboard(statement_id)

    if statement.messages is None:
        address = info[statement.task_type_id]
        answer = f"{address}\nЗаявка №{statement.id}\nот {user.name}\n+{user.phone}"
        return await bot.send_message(
            chat_id=user_id, text=answer, reply_markup=keyboard
        )
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


"""end help functions"""
router = Router()


@router.message(Command("start"))
async def start_(message: Message, state: FSMContext):
    await state.clear()
    user_id = int(message.from_user.id)

    if not crud_users.get_user_auth_by_id(user_id):
        return await message.answer(
            text=texts.start_false_text, reply_markup=keyboards.start_false_keyboard
        )
    if bool(crud_users.read_user(user_id).was_deleted):
        return await message.answer(
            text="Вас удалили из Базы Данных",
            reply_markup=keyboards.start_false_keyboard,
        )
    await message.answer(
        text=texts.start_true_text, reply_markup=keyboards.start_true_keyboard
    )


@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await state.clear()

    user_id = int(callback.from_user.id)
    if not crud_users.get_user_auth_by_id(user_id):
        return await callback.message.answer(
            text=texts.start_false_text, reply_markup=keyboards.start_false_keyboard
        )
    if bool(crud_users.read_user(user_id).was_deleted):
        return await callback.message.answer(
            text="Вас удалили из Базы Данных",
            reply_markup=keyboards.start_false_keyboard,
        )
    await callback.message.answer(
        text=texts.start_true_text, reply_markup=keyboards.start_true_keyboard
    )


"""start user registration"""


class Inn(StatesGroup):
    inn = State()
    phone_number = State()


@router.callback_query(F.data == "gain_access")
async def gain_access(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(
        text=texts.send_inn, keyboards=keyboards.back_keyboard
    )

    await state.set_state(Inn.inn)


@router.message(Inn.inn)
async def inn_message(message: Message, state: FSMContext):
    await state.update_data({"inn": message.text})

    await message.answer(
        text=texts.send_number, reply_markup=keyboards.send_number_keyboard
    )
    await state.set_state(Inn.phone_number)


@router.message(F.contact, Inn.phone_number)
async def phone_number_(message: Message, state: FSMContext):
    user_id = int(message.from_user.id)
    number = str(message.contact.phone_number)
    number = number.replace("+", "")
    data = await state.get_data()

    await state.clear()

    inn = str(data["inn"])

    if not crud_users.get_user_by_inn_and_phone(inn, number):
        return await message.answer(
            text=texts.no_access, reply_markup=keyboards.remove_reply_markup
        )

    crud_users.add_user_id(inn, number, user_id)
    crud_users.change_status(user_id, 1)

    await message.answer(
        text=texts.yes_access, reply_markup=keyboards.remove_reply_markup
    )


"""end user registration"""


@router.callback_query(F.data == "my_statements")
async def my_statements_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    user_id = int(callback.from_user.id)

    user_statements = crud_users.get_user_statements(user_id)
    if user_statements is None:
        return await callback.message.answer(
            text=texts.no_statements_yet, reply_markup=keyboards.back_keyboard
        )
    user_statements = list(map(int, user_statements.split()))
    user_statements = [crud_statements.get_statement_by_id(i) for i in user_statements]
    sort_statements = utils.sort_by_date(user_statements)
    page = 1 if len(sort_statements) != 0 else 0
    await callback.message.answer(
        text=texts.user_statements_text,
        reply_markup=keyboards.user_statements_keyboard(sort_statements, page),
    )


@router.callback_query(F.data.startswith("user_statements_keyboard_data_"))
async def user_statements_keyboard_data_(callback: CallbackQuery):
    await callback.answer()

    user_id = int(callback.from_user.id)
    user_statements = crud_users.get_user_statements(user_id)
    if user_statements is None:
        return await callback.message.answer(
            text=texts.no_statements_yet, reply_markup=keyboards.back_keyboard
        )
    user_statements = list(map(int, user_statements.split()))
    user_statements = [crud_statements.get_statement_by_id(i) for i in user_statements]
    sort_statements = utils.sort_by_date(user_statements)
    page = int(callback.data.split("_")[-1])
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.user_statements_keyboard(sort_statements, page)
    )


@router.callback_query(F.data.startswith("my_user_statements_"))
async def my_user_statements_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    user_id = int(callback.from_user.id)
    statement_id = int(callback.data.split("_")[-1])
    await send_pretty_statement(user_id, statement_id)


"""sent to admin"""


class SentToAdmin(StatesGroup):
    statement_id = State()
    text = State()


@router.callback_query(F.data.startswith("sent_answer_"))
async def sent_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    statement_id = int(callback.data.split("_")[-1])

    await callback.message.answer(
        text=texts.my_statement_answer.format(number=statement_id),
    )
    await state.set_state(SentToAdmin.text)
    await state.update_data({"statement_id": statement_id})


@router.message(SentToAdmin.text)
async def my_statement_sent(
    message: Message, state: FSMContext, album: List[Message] = None
):
    if message.voice:
        return await message.answer(
            text=texts.you_cant_send_voice_messages,
            reply_markup=keyboards.back_keyboard,
        )

    statement_id = (await state.get_data())["statement_id"]

    statement = crud_statements.get_statement_by_id(statement_id)
    if statement.status == 3:
        return await message.answer(
            text=texts.statement_status_completed, reply_markup=keyboards.back_keyboard
        )

    await state.clear()

    lst = create_user_message_function(message=message, album=album)
    if lst == "no format":
        return await message.answer(
            text=texts.no_format_to_create_statement,
            reply_markup=keyboards.back_keyboard,
        )
    if lst == "to_long":
        return await message.answer(
            text=texts.to_long,
            reply_markup=keyboards.back_keyboard,
        )
    data = "{{}}".join(lst)
    multimedia = data
    user_id = int(message.from_user.id)
    type_of_user = "user"
    message_db = MessagesModel(
        user_id=user_id,
        type_of_user=type_of_user,
        multimedia=multimedia,
        date=datetime.now(),
    )
    message_id = crud_messages.create_message(message_db)

    crud_statements.update_messages(statement_id, message_id)

    await state.clear()

    await message.answer(
        text=texts.successfully_sent, reply_markup=keyboards.back_keyboard
    )
    superusers = crud_superusers.get_superadmins()
    if statement.task_type_id == 1:
        superusers += crud_superusers.get_admins()
    else:
        superusers += crud_superusers.get_accountants()

    admin_type = "admin"
    if statement.task_type_id != 1:
        admin_type = "accountant"
    for admin_id in superusers:
        await bot.send_message(
            text=f"Пользователь ответил на заявку «{statement.theme or '№' + str(statement.office_id)}»\nПерейти к ней: /{admin_type}",
            chat_id=admin_id,
        )


"""start new statement"""


class NewStatement(StatesGroup):
    description = State()


@router.callback_query(F.data == "new_statement")
async def new_statement_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(text=texts.new_statement_text)
    await state.set_state(NewStatement.description)


@router.message(NewStatement.description)
async def new_statement_description(
    message: Message, state: FSMContext, album: List[Message] = None
):
    if message.voice:
        return await message.answer(
            text=texts.you_cant_send_voice_messages,
            reply_markup=keyboards.back_keyboard,
        )

    lst = create_user_message_function(message=message, album=album)
    if lst == "no format":
        return await message.answer(
            text=texts.no_format_to_create_statement,
            reply_markup=keyboards.back_keyboard,
        )
    if lst == "to_long":
        return await message.answer(
            text=texts.to_long,
            reply_markup=keyboards.back_keyboard,
        )
    data = "{{}}".join(lst)

    await message.answer(
        text=texts.application_sent_for_moderation,
        reply_markup=keyboards.back_keyboard,
    )

    admins = crud_superusers.get_admins()
    admins += crud_superusers.get_superadmins()
    for admin_id in admins:
        await bot.send_message(
            text="Пользователь оставил новую заявку. /admin", chat_id=admin_id
        )

    user_id = int(message.from_user.id)
    type_of_user = "user"
    multimedia = data

    office_id = crud_users.get_user_offices(user_id).lstrip().rstrip()
    if len(office_id.split(" ")) != 1:
        office_id = None
    else:
        office_id = int(office_id)

    message_db = MessagesModel(
        user_id=user_id,
        type_of_user=type_of_user,
        multimedia=multimedia,
        date=datetime.now(),
    )
    message_id = crud_messages.create_message(message_db)

    statement_db = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=1,
        messages=f"{message_id}",
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=office_id,
    )

    statement_id = crud_statements.create_statement(statement_db)
    crud_users.add_statement(user_id, statement_id)

    await state.clear()


"""end new statement"""
"""start meter readings"""


class LowMeterReadings(StatesGroup):
    data = State()
    readings = State()
    last = State()


class MiddleMeterReadings(StatesGroup):
    meters = State()
    data = State()
    readings = State()
    last = State()


class HighMeterReadings(StatesGroup):
    office = State()
    meters = State()
    data = State()
    readings = State()
    last = State()


@router.callback_query(F.data == "submitting_meter_readings")
async def submit_meter_readings_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    user_id = int(callback.from_user.id)

    offices = crud_users.get_user_offices(user_id)
    print(offices)
    if offices is None:
        return await callback.message.answer(
            text=texts.no_offices_yet, reply_markup=keyboards.back_keyboard
        )
    offices = offices.split()
    """if only one office. else keyboard"""
    if len(offices) == 1:
        office_id = int(offices[0])
        meters = crud_offices.get_meters(office_id)
        meters = meters.split()
        """if only one meter. else keyboard"""
        if len(meters) == 1:
            meter_id = int(meters[0])
            meter_type, unit = crud_meters.get_meter(meter_id)
            data = [office_id, meter_id]
            await state.set_state(LowMeterReadings.data)
            await state.update_data({"data": data})
            await state.set_state(LowMeterReadings.readings)
            return await callback.message.answer(
                text=texts.meter_readings(meter_type, unit)
            )
        """keyboard with meters"""
        meters_names = []
        for meter in meters:
            meters_names.append(
                [crud_meters.get_meter_type_by_id(int(meter)), int(meter)]
            )
        await state.set_state(MiddleMeterReadings.meters)
        return await callback.message.answer(
            text=texts.select_counter_text,
            reply_markup=keyboards.select_counter(meters_names, office_id),
        )
    """keyboard with offices"""
    off = []
    for office_id in offices:
        off.append(
            [
                crud_offices.get_office_address_by_id(int(office_id)),
                crud_offices.get_office_number_by_id(int(office_id)),
                office_id,
            ]
        )

    await callback.message.answer(
        text=texts.submitting_meter_readings_text,
        reply_markup=keyboards.select_offices(off),
    )


"""start high meter readings"""


@router.callback_query(F.data.startswith("office_callback_"))
async def office_callback_function(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    office_id = str(callback.data).split("_")[-1]

    meters = crud_offices.get_meters(office_id).split()
    if len(meters) == 1:
        meter_id = meters[0]
        meter_type, unit = crud_meters.get_meter(meter_id)
        await state.set_state(HighMeterReadings.readings)
        await state.update_data({"data": [office_id, meter_id]})
        return await callback.message.answer(
            text=texts.meter_readings(meter_type, unit)
        )
    meters_names = []
    for meter in meters:
        meters_names.append([crud_meters.get_meter_type_by_id(int(meter)), int(meter)])
    await callback.message.answer(
        text=texts.select_counter_text,
        reply_markup=keyboards.select_high_counter(meters_names, office_id),
    )
    await state.set_state(HighMeterReadings.meters)


@router.callback_query(
    F.data.startswith("high_meter_callback_"), HighMeterReadings.meters
)
async def high_meter_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    meter_id, office_id = map(int, callback.data.split("_")[3:])
    meter_type, unit = crud_meters.get_meter(meter_id)
    await state.update_data({"data": [office_id, meter_id]})
    await state.set_state(HighMeterReadings.readings)
    await callback.message.answer(text=texts.meter_readings(meter_type, unit))


@router.message(HighMeterReadings.readings)
async def low_meter_readings(message: Message, state: FSMContext):
    data = await state.get_data()
    office_id, meter_id = map(int, data["data"])
    readings = message.text
    office_address = crud_offices.get_office_address_by_id(office_id)
    meter_type, unit = crud_meters.get_meter(meter_id)

    await state.update_data({"readings": readings})
    await message.answer(
        text=texts.check_reading(office_address, meter_type, readings, unit),
        reply_markup=keyboards.go_to_send_statement_keyboard_high,
    )
    await state.set_state(HighMeterReadings.last)


@router.callback_query(F.data == "send_it_high", HighMeterReadings.last)
async def send_it_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(
        text=texts.meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )
    user_id = int(callback.from_user.id)
    multimedia = f"text[]None[]{data['readings']}"
    message = MessagesModel(
        user_id=user_id, type_of_user="user", multimedia=multimedia, date=datetime.now()
    )
    message_id = crud_messages.create_message(message)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=2,
        messages=f"{message_id}",
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=int(data["data"][0]),
    )
    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь подал показания счетчиков. /accountant", chat_id=accountant_id
        )


@router.callback_query(F.data == "no_send_it_high", HighMeterReadings.last)
async def no_send_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    await callback.message.answer(
        text=texts.no_meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )


"""end high meter readings"""
"""start middle meter readings"""


@router.callback_query(F.data.startswith("meter_callback_"), MiddleMeterReadings.meters)
async def meter_callback_id(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    meter_id, office_id = map(int, callback.data.split("_")[2:])
    meter_type, unit = crud_meters.get_meter(meter_id)
    await state.update_data({"data": [office_id, meter_id]})
    await state.set_state(MiddleMeterReadings.readings)
    await callback.message.answer(text=texts.meter_readings(meter_type, unit))


@router.message(MiddleMeterReadings.readings)
async def low_meter_readings(message: Message, state: FSMContext):
    data = await state.get_data()
    office_id, meter_id = map(int, data["data"])
    readings = message.text
    office_address = crud_offices.get_office_address_by_id(office_id)
    meter_type, unit = crud_meters.get_meter(meter_id)
    await state.update_data({"readings": readings})
    await message.answer(
        text=texts.check_reading(office_address, meter_type, readings, unit),
        reply_markup=keyboards.go_to_send_statement_keyboard_middle,
    )
    await state.set_state(MiddleMeterReadings.last)


@router.callback_query(F.data == "send_it_middle", MiddleMeterReadings.last)
async def send_it_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(
        text=texts.meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )
    user_id = int(callback.from_user.id)
    multimedia = f"text[]None[]{data['readings']}"
    message = MessagesModel(
        user_id=user_id, type_of_user="user", multimedia=multimedia, date=datetime.now()
    )
    message_id = crud_messages.create_message(message)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=2,
        messages=f"{message_id}",
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=int(data["data"][0]),
    )
    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь подал показания счетчиков. /accountant", chat_id=accountant_id
        )


@router.callback_query(F.data == "no_send_it_middle", MiddleMeterReadings.last)
async def no_send_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    await callback.message.answer(
        text=texts.no_meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )


"""end middle meter readings"""
"""start low meter readings"""


@router.message(LowMeterReadings.readings)
async def low_meter_readings(message: Message, state: FSMContext):
    data = await state.get_data()

    office_id, meter_id = map(int, data["data"])
    readings = message.text
    office_address = crud_offices.get_office_address_by_id(office_id)
    meter_type, unit = crud_meters.get_meter(meter_id)
    await state.update_data({"readings": readings})
    await message.answer(
        text=texts.check_reading(office_address, meter_type, readings, unit),
        reply_markup=keyboards.go_to_send_statement_keyboard,
    )
    await state.set_state(LowMeterReadings.last)


@router.callback_query(F.data == "send_it", LowMeterReadings.last)
async def send_it_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(
        text=texts.meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )
    user_id = int(callback.from_user.id)
    multimedia = f"text[]None[]{data['readings']}"
    message = MessagesModel(
        user_id=user_id, type_of_user="user", multimedia=multimedia, date=datetime.now()
    )
    message_id = crud_messages.create_message(message)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=2,
        messages=f"{message_id}",
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=int(data["data"][0]),
    )
    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь подал показания счетчиков. /accountant", chat_id=accountant_id
        )


@router.callback_query(F.data == "no_send_it", LowMeterReadings.last)
async def no_send_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    await callback.message.answer(
        text=texts.no_meter_readings_sent_text, reply_markup=keyboards.back_keyboard
    )


"""end low meter readings"""
"""end meter readings"""


class RequestForOtherDocumentation(StatesGroup):
    request = State()


@router.callback_query(F.data == "request_for_other_documentation")
async def request_for_other_documentation_callback(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()

    await callback.message.answer(
        text=texts.request_for_other_documentation_text,
        reply_markup=keyboards.back_keyboard,
    )
    await state.set_state(RequestForOtherDocumentation.request)


@router.message(RequestForOtherDocumentation.request)
async def request_for_other_documentation_request(
    message: Message, state: FSMContext, album: List[Message] = None
):
    if message.voice:
        return await message.answer(
            text=texts.you_cant_send_voice_messages,
            reply_markup=keyboards.back_keyboard,
        )
    lst = create_user_message_function(message=message, album=album)
    if lst == "no format":
        return await message.answer(
            text=texts.no_format_to_create_statement,
            reply_markup=keyboards.back_keyboard,
        )
    if lst == "to_long":
        return await message.answer(
            text=texts.to_long,
            reply_markup=keyboards.back_keyboard,
        )
    data = "{{}}".join(lst)

    await message.answer(
        text=texts.documentation_sent, reply_markup=keyboards.back_keyboard
    )

    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь оставил заявку на запрос прочей документации. /accountant",
            chat_id=accountant_id,
        )

    user_id = int(message.from_user.id)
    type_of_user = "user"
    multimedia = data

    office_id = crud_users.get_user_offices(user_id).lstrip().rstrip()
    if len(office_id.split(" ")) != 1:
        office_id = None
    else:
        office_id = int(office_id)

    message_db = MessagesModel(
        user_id=user_id,
        type_of_user=type_of_user,
        multimedia=multimedia,
        date=datetime.now(),
    )
    message_id = crud_messages.create_message(message_db)

    statement_db = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=3,
        messages=f"{message_id}",
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=office_id,
    )

    statement_id = crud_statements.create_statement(statement_db)
    crud_users.add_statement(user_id, statement_id)

    await state.clear()


@router.callback_query(F.data == "ku_accuracy")
async def ku_accuracy_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    user_id = int(callback.from_user.id)
    office_id = crud_users.get_user_offices(user_id).lstrip().rstrip()
    if len(office_id.split(" ")) != 1:
        office_id = None
    else:
        office_id = int(office_id)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=4,
        messages=None,
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=office_id,
    )

    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    await callback.message.answer(
        text=texts.ku_text, reply_markup=keyboards.back_keyboard
    )
    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь запросил начисление КУ. /accountant", chat_id=accountant_id
        )


@router.callback_query(F.data == "rent_accuracy")
async def rent_accuracy_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    user_id = int(callback.from_user.id)
    office_id = crud_users.get_user_offices(user_id).lstrip().rstrip()
    if len(office_id.split(" ")) != 1:
        office_id = None
    else:
        office_id = int(office_id)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=5,
        messages=None,
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=office_id,
    )

    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    await callback.message.answer(
        text=texts.rent_accuracy_text, reply_markup=keyboards.back_keyboard
    )
    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    for accountant_id in accountant:
        await bot.send_message(
            text="Пользователь запросил начисление аренды. /accountant", chat_id=accountant_id
        )


@router.callback_query(F.data == "request_for_reconciliation_report")
async def request_for_reconciliation_report_callback(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.clear()
    user_id = int(callback.from_user.id)
    office_id = crud_users.get_user_offices(user_id).lstrip().rstrip()
    if len(office_id.split(" ")) != 1:
        office_id = None
    else:
        office_id = int(office_id)
    statement = StatementsModel(
        user_id=user_id,
        admin_id=None,
        task_type_id=6,
        messages=None,
        date_creation=datetime.now(),
        date_run=None,
        date_finish=None,
        theme=None,
        status=1,
        office_id=office_id,
    )

    statement_id = crud_statements.create_statement(statement)
    crud_users.add_statement(user_id, statement_id)

    await callback.message.answer(
        text=texts.request_for_reconciliation_report_text,
        reply_markup=keyboards.back_keyboard,
    )

    accountant = crud_superusers.get_accountants()
    accountant += crud_superusers.get_superadmins()
    print(accountant)
    for accountant_id in accountant:
        try:
            await bot.send_message(
                text="Пользователь оставил запрос акта и сверки. /accountant",
                chat_id=accountant_id
            )
        except:
            print(accountant_id)


@router.message(Command("create_me"))
async def create_me(message: Message):
    user = UsersModel(
        user_id=None,
        name="Амир Князев",
        phone="79393167376",
        inn="123",
        due_date=1,
        meter_notification=True,
        rent_notification=True,
        auth=False,
        was_deleted=False,
        statements=None,
        offices="1 2",
    )
    crud_users.create_user(user)
