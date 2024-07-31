from pydantic import BaseModel


class Users(BaseModel):
    user_id: int | None
    name: str
    phone: str
    inn: str
    due_date: int
    meter_notification: bool
    rent_notification: bool
    auth: bool
    was_deleted: bool
    statements: str | None
    offices: str | None
