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


def create_start_db():
    # TODO: creating default database
    if crud_task_types.get_task_type_by_id(1) is not None:
        return ":(("

    meters = {
        1: ["Электричество", "кВт"],
        2: ["Вода", "м3"]
    }

    for k in meters.values():
        meter = Meters(
            meter_type=k[0],
            unit=k[1]
        )

        crud_meters.create_meter(meter)

    task_types_dict = {
        1: "Заявка",
        2: "Подача показаний счетчиков",
        3: "Запрос прочей документации",
        4: "Начисление КУ",
        5: "Начисление аренды",
        6: "Запрос акта сверки",
    }

    for task_type in task_types_dict.values():
        task_type_model = TaskTypes(
            task_type=task_type
        )
        crud_task_types.create_task_type(task_type_model)

    office1 = Offices(
        address="ул. Раскольникова, 29",
        office_number=5,
        coder_number=None,
        meters="1 2"
    )

    office2 = Offices(
        address="просп. Сююмбике, 40",
        office_number=9,
        coder_number=None,
        meters="1"
    )

    office3 = Offices(
        address="Пролетарский пр., 10Б",
        office_number=17,
        coder_number=None,
        meters="2"
    )

    crud_offices.create_office(office1)
    crud_offices.create_office(office2)
    crud_offices.create_office(office3)

    user = Users(
        user_id=None,
        name="Альберт",
        phone="79093074556",
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

    superuser = SuperUsers(
        user_id=6980676960,
        name="Luka Math",
        superuser_type=1
    )
    crud_superusers.create_superuser(superuser)

    # superuser = SuperUsers(
    #     user_id=85288369,
    #     name="Егор",
    #     superuser_type=1
    # )
    # crud_superusers.create_superuser(superuser)

    superuser = SuperUsers(
        user_id=128518307,
        name="Альберт М",
        superuser_type=1
    )
    crud_superusers.create_superuser(superuser)
