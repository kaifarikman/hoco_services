from datetime import datetime


def sort_statements(statements):
    new_statements = []
    for statement in statements:
        if statement.status != 3:
            new_statements.append(statement)
    new_statements = sorted(new_statements, key=lambda x: x.date_creation)[::-1]
    return new_statements


def convert_date(date):
    return date.strftime('%d.%m.%Y, %H:%M')
