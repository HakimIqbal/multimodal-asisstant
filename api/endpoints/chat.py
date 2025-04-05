from fastapi import APIRouter, Form
from src.chat import generate_response

router = APIRouter()

@router.post("/ask/")
async def ask_chatbot(query: str = Form(...)):
    response = generate_response(query)
    return {"query": query, "answer": response}