from pydantic import BaseModel


class SuperUsers(BaseModel):
    user_id: int
    name: str
    superuser_type: int
