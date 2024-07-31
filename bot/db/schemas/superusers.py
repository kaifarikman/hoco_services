from bot.db.db import Base
from sqlalchemy import Column, Integer, String


class SuperUsers(Base):
    __tablename__ = "superusers"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    superuser_type = Column(Integer)
