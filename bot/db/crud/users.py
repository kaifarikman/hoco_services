from bot.db.models.users import Users
from bot.db.schemas.users import Users as UsersDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine

import bot.db.crud.offices as crud_offices


def create_user(user: Users):
    session = sessionmaker(engine)()
    try:
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
    finally:
        session.close()


def read_user(user_id):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(user_id=user_id).first()

        return query
    finally:
        session.close()


def get_user_auth_by_id(user_id: int):
    user = read_user(user_id)
    if not user:
        return False
    return bool(user.auth)


def get_user_by_inn_and_phone(inn, number):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(inn=inn, phone=number).first()
        return bool(query)
    finally:
        session.close()


def get_user_by_phone_number(phone_number):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(phone=phone_number).first()

        if query is None:
            return None
        return query.id

    finally:
        session.close()


def change_status(user_id, status):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(user_id=user_id).first()
        query.auth = status
        session.commit()
    finally:
        session.close()


def add_user_id(inn, number, user_id):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(inn=inn, phone=number).first()
        query.user_id = user_id
        session.commit()
    finally:
        session.close()


def add_statement(user_id, statement_id):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(user_id=user_id).first()
        if query.statements is None:
            query.statements = ""
        query.statements += " " + statement_id
        session.commit()
    finally:
        session.close()


def get_user_statements(user_id):
    user = read_user(user_id)
    return user.statements


def get_user_offices(user_id):
    user = read_user(user_id)
    return user.offices


def get_all_users():
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).all()
        return query
    finally:
        session.close()


def delete_user(id_):
    session = sessionmaker(engine)()
    try:
        query = session.query(UsersDB).filter_by(id=id_).first()
        query.was_deleted = True
        session.commit()
    finally:
        session.close()


def get_users_by_address(address):
    users = get_all_users()
    new_users = []
    for user in users:
        offices = list(map(int, get_user_offices(user.user_id).split()))
        for office_id in offices:
            office_address = crud_offices.get_office_address_by_id(office_id)
            if office_address == address:
                new_users.append(user)
    return new_users
