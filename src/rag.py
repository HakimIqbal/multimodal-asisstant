from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from models import llm, vector_store
from config import LANGSMITH_TRACING

# Template prompt yang lebih ketat
prompt_template = """Gunakan hanya informasi dari konteks berikut untuk menjawab pertanyaan. Jika konteks tidak cukup untuk menjawab, katakan "Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
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
    # Ambil dokumen relevan dari retriever
    docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
    if not docs or all(doc.page_content.strip() == "" for doc in docs):
        return "Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
    result = rag_chain.invoke({"query": question})
    return result["result"]