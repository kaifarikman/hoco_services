from datetime import datetime
from bot.db.schemas.users import Users as UsersDB


def sort_statements(statements):
    new_statements = []
    for statement in statements:
        if statement.task_type_id == 1 and statement.status != 3:
            new_statements.append(statement)
    new_statements = sorted(new_statements, key=lambda x: x.date_creation)[::-1]
    return new_statements


def convert_date(date: datetime):
    return date.strftime("%d.%m.%Y, %H:%M")


def get_newsletters(users: list[UsersDB]):
    newsletters = list()
    for user in users:
        if user.was_deleted:
            continue
        offices = user.offices.split()
        for office in offices:
            newsletters.append([office, user.user_id])
    return newsletters
