from bot.db.models.offices import Offices
from bot.db.schemas.offices import Offices as OfficesDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_office(office_db: Offices):
    session = sessionmaker(engine)()
    office = OfficesDB(
        address=office_db.address,
        office_number=office_db.office_number,
        coder_number=office_db.coder_number,
        meters=office_db.meters,
    )
    session.add(office)
    session.commit()


def read_office(office_id: int):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(
        id=office_id
    ).first()
    return query.address, query.office_number, query.coder_number, query.meters


def update_office(office_id: int, *args):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(
        id=office_id
    ).first()
    # args - update_parametr


def delete_office(office_id: int):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(id=office_id)
    query.delete()
    session.commit()

def get_meters(office_id):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(
        id=office_id
    ).first()
    return str(query.meters)


def get_office_address_by_id(office_id):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(
        id=office_id
    ).first()
    return str(query.address)


def get_office_number_by_id(office_id):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(
        id=office_id
    ).first()
    return str(query.office_number)
