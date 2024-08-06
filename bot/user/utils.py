from bot.db.schemas.statements import Statements
from datetime import datetime


def sort_by_date(statements: list[Statements]):
    return sorted(statements, key=lambda x: x.date_creation)[::-1]


def convert_date(date: datetime):
    return date.strftime("%d.%m.%Y, %H:%M")
