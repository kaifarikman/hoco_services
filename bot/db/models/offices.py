from pydantic import BaseModel


class Offices(BaseModel):
    address: str
    office_number: str
    coder_number: str | None
    meters: str | None
