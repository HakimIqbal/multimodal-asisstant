from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from src.rag import rag_chain
from literalai import LiteralClient

# Inisialisasi LiteralAI untuk evaluasi output
literal_client = LiteralClient(api_key="YOUR_LITERALAI_API_KEY")

# Inisialisasi memory untuk percakapan
memory = ConversationBufferMemory()

# Template prompt untuk Assistant
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Context: {context}\n\nQuestion: {question}\n\nAnswer:"
)

def generate_response(question: str):
    # Ambil konteks dari RAG
    rag_result = rag_chain({"query": question})
    context = rag_result["answer"]
    
    # Gabungkan dengan memory
    memory.save_context({"input": question}, {"output": context})
    
    # Generate jawaban
    prompt = prompt_template.format(context=context, question=question)
    response = rag_chain.llm(prompt)
    
    # Evaluasi kualitas output dengan LiteralAI
    literal_client.log({"input": question, "output": response})
    
    return response