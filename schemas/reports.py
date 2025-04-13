from typing import List

from pydantic import BaseModel, Field
from sqlalchemy.sql.annotation import Annotated


class ReportBase(BaseModel):
    id: Annotated[int]
    title: Annotated[
        str,
        Field(
            min_length=2, max_length=100, description="Название отчета"
        )
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            min_length=2,
            max_length=500,
            description="Описание (необязательно, от 2 до 500 символов)"
        )
    ]
    email: Annotated[
        str,
        Field(min_length=2, max_length=50, description="Почта (от 2 до 50 символов)")
    ]
    status: Annotated[
        str,
        Field(min_length=2, max_length=50, description="Статус (от 2 до 50 символов)")
    ]
    file_ids: Annotated[
        List[int]
    ]

    class Config:
        arbitrary_types_allowed = True


class FileResponse(BaseModel):
    id: int
    name: str
    extension: str
    url: str
