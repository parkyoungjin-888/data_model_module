from enum import Enum
from typing import Optional
from beanie import PydanticObjectId
from pydantic import Field, validator
from datetime import datetime

from data_model_module.beanie_data_model.custom_base_model import CustomBaseModel


class Image(CustomBaseModel):
    device_id: str
    name: str
    timestamp: float
    event_datetime: datetime
    process_datetime: datetime
    width: int
    height: int
    img_path: str


class ProjectImage(CustomBaseModel):
    id: PydanticObjectId = Field(alias='_id')
    name: str
    img_collection: Optional[str | None] = None

    @validator('id', pre=False)
    def convert_object_id2str(cls, value):
        return str(value)
