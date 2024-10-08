from bot.db.models.superusers import SuperUsers
from bot.db.schemas.superusers import SuperUsers as SuperUsersDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_superuser(superuser: SuperUsers):
    session = sessionmaker(engine)()
    try:
        superuser_db = SuperUsersDB(
            user_id=superuser.user_id,
            name=superuser.name,
            superuser_type=superuser.superuser_type,
        )
        session.add(superuser_db)
        session.commit()

        return superuser_db.id
    finally:
        session.close()


def read_superuser(superuser_id: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(id=superuser_id).first()

        return query
    finally:
        session.close()


def update_superuser(superuser_id: int, superuser_type: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(id=superuser_id).first()
        query.superuser_type = superuser_type
        session.commit()
    finally:
        session.close()


def delete_superuser(superuser_id: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(id=superuser_id)
        query.delete()
        session.commit()
    finally:
        session.close()


def get_superuser(user_id, access_roles):
    session = sessionmaker(engine)()
    try:
        query = (
            session.query(SuperUsersDB)
            .filter_by(
                user_id=user_id,
            )
            .first()
        )

        if query is None:
            return False

        if query.superuser_type not in access_roles:
            return False
        return True
    finally:
        session.close()


def get_superuser_role(user_id):
    session = sessionmaker(engine)()
    try:
        query = (
            session.query(SuperUsersDB)
            .filter_by(
                user_id=user_id,
            )
            .first()
        )

        if query is None:
            return False
        return query.superuser_type
    finally:
        session.close()


def get_superusers():
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).all()

        return query
    finally:
        session.close()


def get_superadmins() -> list[int]:
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(superuser_type=1).all()

        return [i.user_id for i in query]
    finally:
        session.close()


def get_admins() -> list[int]:
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(superuser_type=2).all()

        return [i.user_id for i in query]
    finally:
        session.close()


def get_accountants() -> list[int]:
    session = sessionmaker(engine)()
    try:
        query = session.query(SuperUsersDB).filter_by(superuser_type=3).all()

        return [i.user_id for i in query]
    finally:
        session.close()
