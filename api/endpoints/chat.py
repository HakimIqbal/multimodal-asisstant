from fastapi import APIRouter
from pydantic import BaseModel
from src.chat import chat_with_memory

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat/")
async def chat(request: ChatRequest):
    response = chat_with_memory(request.question)
    return {"question": request.question, "response": response}