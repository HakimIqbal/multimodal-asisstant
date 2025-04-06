from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from models import llm, vector_store
from config import LANGSMITH_TRACING

prompt_template = """System: Saya adalah Assistant yang hanya menjawab berdasarkan dokumen yang diunggah melalui RAG System + OCR. 
Saya tidak akan menggunakan pengetahuan eksternal di luar dokumen tersebut. Jika informasi tidak ada, saya akan memberitahu Anda.
Context: {context}
Question: {question}
Answer:"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": PROMPT}
)

def query_rag(question: str):
    if LANGSMITH_TRACING:
        print(f"Melacak query '{question}' di LangSmith.")
    docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
    if not docs or all(doc.page_content.strip() == "" for doc in docs):
        return "Assistant: Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
    result = rag_chain.invoke({"query": question})
    return result["result"]