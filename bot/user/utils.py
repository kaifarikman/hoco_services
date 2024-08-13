from bot.db.schemas.statements import Statements
from datetime import datetime, timedelta


def sort_by_date(statements: list[Statements]):
    now = datetime.now() + timedelta(hours=3)
    new_statements = []
    for statement in statements:
        if statement.date_finish is None:
            new_statements.append(statement)
        else:
            if statement.date_finish + timedelta(hours=14) > now:
                new_statements.append(statement)
            else:
                print("___"*10)

    return sorted(new_statements, key=lambda x: x.date_creation)[::-1]


def convert_date(date: datetime):
    return date.strftime("%d.%m.%Y, %H:%M")
