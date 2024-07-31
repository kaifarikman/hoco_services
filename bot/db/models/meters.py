from pydantic import BaseModel


class Meters(BaseModel):
    meter_type: str
    unit: str