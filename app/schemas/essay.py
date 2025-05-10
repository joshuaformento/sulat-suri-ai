from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EssayBase(BaseModel):
    title: str
    content: str
    topic: Optional[str] = None

class EssayCreate(EssayBase):
    pass

class Essay(EssayBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True