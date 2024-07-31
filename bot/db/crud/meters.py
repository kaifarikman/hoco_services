from bot.db.models.meters import Meters
from bot.db.schemas.meters import Meters as MetersDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_meter(meter: Meters):
    session = sessionmaker(engine)()
    meter_db = MetersDB(
        meter_type=meter.meter_type,
        unit=meter.unit,
    )
    session.add(meter_db)
    session.commit()


def read_meter(meter_id):
    session = sessionmaker(engine)()
    query = session.query(MetersDB).filter_by(
        id=meter_id
    ).first()
    return query.meter_type, query.unit


def update_meter(meter_id: int, meter_type: str, unit: str):
    session = sessionmaker(engine)()
    query = session.query(MetersDB).filter_by(
        id=meter_id
    ).first()
    query.meter_type = meter_type
    query.unit = unit
    session.commit()


def delete_meter(meter_id: int):
    session = sessionmaker(engine)()
    query = session.query(MetersDB).filter_by(id=meter_id)
    query.delete()
    session.commit()


def get_meter(meter_id):
    session = sessionmaker(engine)()
    query = session.query(MetersDB).filter_by(
        id=meter_id
    ).first()
    return query.meter_type, query.unit


def get_meter_type_by_id(meter_id):
    session = sessionmaker(engine)()
    query = session.query(MetersDB).filter_by(
        id=meter_id
    ).first()
    return query.meter_type
