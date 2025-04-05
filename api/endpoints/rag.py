from fastapi import APIRouter
from pydantic import BaseModel
from src.rag import query_rag

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/query/")
async def query(request: QueryRequest):
    answer = query_rag(request.question)
    return {"question": request.question, "answer": answer}