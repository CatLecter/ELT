from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class Id(BaseModel):
    id: UUID


class StateMap(Id):
    updated_at: datetime
    need_load: Optional[bool] = True
    table_name: Optional[str] = ""


class Index(Id):
    imdb_rating: Optional[float]
    title: Optional[str]
    description: Optional[str]
    genre: Optional[list]
    director: Optional[list]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
