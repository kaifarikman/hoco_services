from bot.db.models.statements import Statements
from bot.db.schemas.statements import Statements as StatementsDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_statement(statement: Statements):
    session = sessionmaker(engine)()
    try:
        statement_db = StatementsDB(
            user_id=statement.user_id,
            admin_id=statement.admin_id,
            task_type_id=statement.task_type_id,  # айдишки из БД "TaskType"
            messages=statement.messages,  # айдишки из БД "Messages"
            date_creation=statement.date_creation,
            date_run=statement.date_run,
            date_finish=statement.date_finish,
            theme=statement.theme,
            status=statement.status,
            office_id=statement.office_id,
        )
        session.add(statement_db)
        session.commit()

        return str(statement_db.id)
    finally:
        session.close()


def get_statements():
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).all()

        return query
    finally:
        session.close()


def get_statement_by_id(statement_id):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        return query
    finally:
        session.close()


def update_theme(statement_id, theme):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        query.theme = theme
        session.commit()
    finally:
        session.close()


def update_messages(statement_id, message_id):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        if query.messages is None:
            query.messages = str(message_id)
        else:
            query.messages += " " + str(message_id)
        session.commit()
    finally:
        session.close()


def change_status(statement_id, status):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        query.status = status
        session.commit()
    finally:
        session.close()


def set_date_run(statement_id, date):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        query.date_run = date
        session.commit()
    finally:
        session.close()


def set_date_finish(statement_id, date):
    session = sessionmaker(engine)()
    try:
        query = session.query(StatementsDB).filter_by(id=statement_id).first()
        query.date_finish = date
        session.commit()
    finally:
        session.close()
