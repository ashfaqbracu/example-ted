from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message to send to the chat assistant", min_length=1)
    user_id: str = Field(..., description="The user's unique identifier (required for chat history collection)", min_length=1)

class ChatResponse(BaseModel):
    response: str
    status: str

class StatusResponse(BaseModel):
    status: str
    message: str
    data_summary: Optional[str] = None

class CreateHistoryRequest(BaseModel):
    userId: str = Field(..., description="The user's unique identifier", min_length=1)
    human: str = Field(..., description="The human/user message", min_length=1)
    assistant: str = Field(..., description="The assistant's response", min_length=1)

class HistoryResponse(BaseModel):
    userId: str
    chat_history: List[Dict[str, Any]]
    total_conversations: int
    status: str
