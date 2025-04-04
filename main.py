# Entry point utama (Menjalankan API & UI)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import MistralChatbot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
chatbot = MistralChatbot(model_path="models/mistral-7b-instruct-v0.1.Q3_K_M.gguf")

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = chatbot.generate_response(request.question)
    return {"response": response}

@app.get("/")
def home():
    return {"message": "Mistral Chatbot API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
