from bot.db.models.messages import Messages
from bot.db.schemas.messages import Messages as MessagesDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_message(message: Messages):
    session = sessionmaker(engine)()
    message_db = MessagesDB(
        user_id=message.user_id,
        type_of_user=message.type_of_user,
        multimedia=message.multimedia,
        date=message.date,
    )
    session.add(message_db)
    session.commit()
    session.close()
    return message_db.id


def read_message(message_id: int):
    session = sessionmaker(engine)()
    query = session.query(MessagesDB).filter_by(id=message_id).first()
    session.close()
    return query


def update_message(message_id: int, new_multimedia: str):
    session = sessionmaker(engine)()
    query = session.query(MessagesDB).filter_by(id=message_id).first()
    query.multimedia = new_multimedia
    session.commit()
    session.close()


def delete_message(message_id: int):
    session = sessionmaker(engine)()
    query = session.query(MessagesDB).filter_by(id=message_id)
    query.delete()
    session.commit()
    session.close()
