from fastapi import APIRouter
from pydantic import BaseModel
from src.rag import query_rag

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    chat_history: list = None  # Riwayat percakapan (opsional)

@router.post("/query/")
async def query(request: QueryRequest):
    answer, updated_history = query_rag(request.question, request.chat_history)
    return {"question": request.question, "answer": answer, "chat_history": updated_history}