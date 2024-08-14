from bot.db.models.task_types import TaskTypes
from bot.db.schemas.task_types import TaskTypes as TaskTypesDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def create_task_type(task_type_: TaskTypes):
    session = sessionmaker(engine)()
    try:
        task_type_db = TaskTypesDB(task_type=task_type_.task_type)
        session.add(task_type_db)
        session.commit()
    finally:
        session.close()


def get_task_type_by_id(task_type_id: int):
    session = sessionmaker(engine)()
    try:
        query = session.query(TaskTypesDB).filter_by(id=task_type_id).first()

        if query:
            return query.task_type
        return None
    finally:
        session.close()
