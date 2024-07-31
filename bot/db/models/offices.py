from pydantic import BaseModel
from datetime import time


class Offices(BaseModel):
    address: str
    office_number: int
    coder_number: str | None
    meters: str | None
