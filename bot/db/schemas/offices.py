from bot.db.db import Base
from sqlalchemy import Column, Integer, String


class Offices(Base):
    __tablename__ = "offices"
    id = Column(Integer, autoincrement=True, primary_key=True)
    address = Column(String)
    office_number = Column(String)
    coder_number = Column(String)
    meters = Column(String)  # айдишки из БД "Meters"
