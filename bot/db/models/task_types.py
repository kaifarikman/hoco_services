from pydantic import BaseModel


class TaskTypes(BaseModel):
    task_type: str