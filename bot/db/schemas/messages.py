from bot.db.db import Base
from sqlalchemy import Column, Integer, String, DateTime


class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    type_of_user = Column(String)
    multimedia = Column(String)
    date = Column(DateTime)
