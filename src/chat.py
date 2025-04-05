from langchain.memory import ConversationBufferMemory
from models import llm

memory = ConversationBufferMemory()

def chat_with_memory(query: str):
    # Simpan percakapan ke memory
    memory.save_context({"input": query}, {"output": ""})
    response = llm.invoke(query)
    memory.save_context({"input": query}, {"output": response.content})
    return response.content