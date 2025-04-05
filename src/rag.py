from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from models import llm, vector_store
from config import LANGSMITH_TRACING

# Template prompt untuk RAG
prompt_template = """Context: {context}
Question: {question}
Answer:"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Inisialisasi chain RAG
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": PROMPT}
)

def query_rag(question: str):
    if LANGSMITH_TRACING:
        # LangSmith akan otomatis melacak eksekusi chain ini karena tracing sudah diaktifkan di config
        print(f"Melacak query '{question}' di LangSmith.")
    return rag_chain.run(question)