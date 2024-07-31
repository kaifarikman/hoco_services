from pydantic import BaseModel
from datetime import datetime


class Messages(BaseModel):
    user_id: int
    type_of_user: str
    multimedia: str
    date: datetime
