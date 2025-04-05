from langchain.chains import RetrievalQA
from langchain.llms import CTransformers
from src.vector_db import vector_store
from config import Config

llm = CTransformers(
    model=Config.MODEL_PATH,
    model_type="mistral",
    config={"gpu_layers": 0, "context_length": 4096}
)

# Inisialisasi RetrievalQA dengan LangChain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

def query_rag(question: str):
    result = rag_chain({"query": question})
    return {
        "answer": result["result"],
        "sources": [doc.metadata["source"] for doc in result["source_documents"]]
    }