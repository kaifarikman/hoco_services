from datetime import datetime


def sort_statements(statements):
    new_statements = []
    for statement in statements:
        if statement.status != 3:
            new_statements.append(statement)
    new_statements = sorted(new_statements, key=lambda x: x.date_creation)[::-1]
    return new_statements


def convert_date_(date):
    return date.strftime("%d.%m.%Y %H:%M")


def convert_date(date: datetime):
    return date.strftime("%d.%m.%Y, %H:%M")


def get_newsletters(users):
    newsletters = list()
    for user in users:
        if user.was_deleted:
            continue
        if user.offices is None:
            continue
        offices = user.offices.split()
        for office in offices:
            newsletters.append([office, user.user_id])
    return newsletters
