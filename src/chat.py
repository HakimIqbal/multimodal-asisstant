from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from models import llm
from config import LANGSMITH_TRACING

memory = ConversationBufferMemory(
    chat_memory=InMemoryChatMessageHistory(),
    return_messages=True
)

def chat_with_memory(query: str):
    if LANGSMITH_TRACING:
        print(f"Melacak chat query '{query}' di LangSmith.")
    memory.save_context({"input": query}, {"output": ""})
    response = llm.invoke(query)
    memory.save_context({"input": query}, {"output": response.content})
    return response.content