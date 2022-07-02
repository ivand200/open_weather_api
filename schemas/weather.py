from typing import List, Optional

from pydantic import BaseModel, validator, ValidationError, Field

from datetime import datetime


class CurrentWeather(BaseModel):
    place: str
    today: str
    temperature: float
    wind: float
    description: str

    # @validator("today", pre=True)
    # def check_today_date(cls, value):  # YYYY-MM-DD
    #     return datetime.date.today.strftime(str(value), "%d-%m-%Y")

    class Config:
        orm_mode = True
