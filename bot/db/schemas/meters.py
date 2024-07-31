from bot.db.db import Base
from sqlalchemy import Column, Integer, String


class Meters(Base):
    __tablename__ = "meters"
    id = Column(Integer, autoincrement=True, primary_key=True)
    meter_type = Column(String)
    unit = Column(String)
