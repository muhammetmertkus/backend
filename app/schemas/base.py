from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class BaseSchema(BaseModel):
    """Temel şema sınıfı."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 