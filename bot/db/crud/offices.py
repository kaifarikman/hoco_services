from bot.db.models.offices import Offices
from bot.db.schemas.offices import Offices as OfficesDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_office(office_db: Offices):
    session = sessionmaker(engine)()
    try:
        office = OfficesDB(
            address=office_db.address,
            office_number=office_db.office_number,
            coder_number=office_db.coder_number,
            meters=office_db.meters,
        )
        session.add(office)
        session.commit()

        return office.id
    finally:
        session.close()


def read_office(office_id: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(OfficesDB).filter_by(id=office_id).first()
        return query
    finally:
        session.close()


def update_office(office_id: int, *args):
    session = sessionmaker(engine)()
    query = session.query(OfficesDB).filter_by(id=office_id).first()
    session.close()
    # args - update_parametr


def delete_office(office_id: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(OfficesDB).filter_by(id=office_id)
        query.delete()
        session.commit()
    finally:
        session.close()


def get_meters(office_id):
    office = read_office(office_id)
    return office.meters


def get_office_address_by_id(office_id):
    office = read_office(office_id)
    return office.address


def get_office_number_by_id(office_id):
    office = read_office(office_id)
    return office.office_number
