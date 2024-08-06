from bot.db.db import Base
from sqlalchemy import Column, Integer, String, Boolean


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    phone = Column(String)
    inn = Column(String)
    due_date = Column(Integer)
    meter_notification = Column(Boolean)
    rent_notification = Column(Boolean)
    auth = Column(Boolean)
    was_deleted = Column(Boolean)
    statements = Column(String)  # айдишки из БД "Заявки"
    offices = Column(String)  # айдишки из БД "Офисы"
