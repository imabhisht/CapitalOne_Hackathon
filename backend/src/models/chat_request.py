from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class Location(BaseModel):
    longitude: float
    latitude: float


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    user_location: Optional[Location] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    content: str
    is_complete: bool = False