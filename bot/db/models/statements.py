from pydantic import BaseModel
from datetime import datetime


class Statements(BaseModel):
    user_id: int
    admin_id: int | None
    task_type_id: int
    messages: str | None
    date_creation: datetime
    date_run: datetime | None
    date_finish: datetime | None
    theme: str | None
    status: int
    office_id: int | None  # None if user have more than 1 office
