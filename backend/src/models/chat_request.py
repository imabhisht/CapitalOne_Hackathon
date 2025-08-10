from typing import Optional
from pydantic import BaseModel


class Location(BaseModel):
    longitude: float
    latitude: float


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    user_location: Optional[Location] = None

class ChatResponse(BaseModel):
    content: str
    is_complete: bool = False