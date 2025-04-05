from langchain.memory import ConversationBufferMemory
from models import llm
from config import LANGSMITH_TRACING

memory = ConversationBufferMemory()

def chat_with_memory(query: str):
    if LANGSMITH_TRACING:
        print(f"Melacak chat query '{query}' di LangSmith.")
    # Simpan percakapan ke memory
    memory.save_context({"input": query}, {"output": ""})
    response = llm.invoke(query)
    memory.save_context({"input": query}, {"output": response.content})
    return response.content