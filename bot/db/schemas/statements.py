from bot.db.db import Base
from sqlalchemy import Column, Integer, String, DateTime


class Statements(Base):
    __tablename__ = "statements"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    admin_id = Column(Integer)
    task_type_id = Column(Integer)  # айдишки из БД "TaskType"
    messages = Column(String)  # айдишки из БД "Messages"
    date_creation = Column(DateTime)
    date_run = Column(DateTime)
    date_finish = Column(DateTime)
    theme = Column(String)
    status = Column(Integer)
    office_id = Column(Integer)

    def __repr__(self):
        return str(self.id)
