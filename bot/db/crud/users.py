from bot.db.models.users import Users
from bot.db.schemas.users import Users as UsersDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_user(user: Users):
    session = sessionmaker(engine)()
    user_db = UsersDB(
        user_id=user.user_id,
        name=user.name,
        phone=user.phone,
        inn=user.inn,
        due_date=user.due_date,
        meter_notification=user.meter_notification,
        rent_notification=user.rent_notification,
        auth=user.auth,
        was_deleted=user.was_deleted,
        statements=user.statements,
        offices=user.offices,
    )
    session.add(user_db)
    session.commit()


def read_user(user_id):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    return query


def get_user_auth_by_id(user_id: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    if not query:
        return False
    return bool(query.auth)


def get_user_by_inn_and_phone(inn, number):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        inn=inn, phone=number
    ).first()
    return bool(query)


def change_status(user_id, status):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    query.auth = status
    session.commit()


def add_user_id(inn, number, user_id):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        inn=inn, phone=number
    ).first()
    query.user_id = user_id
    session.commit()


def add_statement(user_id, statement_id):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    if query.statements is None:
        query.statements = ""
    query.statements += " " + statement_id
    session.commit()


def get_user_statements(user_id):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    return query.statements


def get_user_offices(user_id):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(
        user_id=user_id
    ).first()
    return query.offices
