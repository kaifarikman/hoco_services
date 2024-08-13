from datetime import datetime
from bot.db.schemas.users import Users as UsersDB
import bot.db.crud.offices as crud_offices


def sort_statements(statements):
    new_statements = []
    for statement in statements:
        if statement.task_type_id == 1 and statement.status != 3:
            new_statements.append(statement)
    new_statements = sorted(new_statements, key=lambda x: x.date_creation)[::-1]
    return new_statements


def convert_date(date: datetime):
    return date.strftime("%d.%m.%Y, %H:%M")


def get_addresses(users: list[UsersDB]):
    addresses = list()
    for user in users:
        if user.was_deleted:
            continue
        offices = list(map(int, user.offices.split()))
        for office in offices:
            address = crud_offices.get_office_address_by_id(int(office))
            if address is not None and address not in addresses:
                addresses.append(address)
    return addresses
