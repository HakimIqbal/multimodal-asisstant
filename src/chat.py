from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.callbacks.manager import CallbackManager
from models import llm
from config import LANGSMITH_TRACING

memory = ConversationBufferMemory(
    chat_memory=InMemoryChatMessageHistory(),
    return_messages=True
)

def chat_with_memory(query: str):
    if LANGSMITH_TRACING:
        print(f"System: Melacak chat query '{query}' di LangSmith.")
    
    callback_manager = CallbackManager([]) if LANGSMITH_TRACING else None
    memory.save_context({"input": query}, {"output": ""})
    response = llm.invoke(query, callback_manager=callback_manager)
    memory.save_context({"input": query}, {"output": response.content})
    return response.content