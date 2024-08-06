from bot.db.db import Base
from sqlalchemy import Column, Integer, String


class TaskTypes(Base):
    __tablename__ = "task_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String)
