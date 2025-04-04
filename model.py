import os
from ctransformers import AutoModelForCausalLM

# Load Model Mistral dengan optimasi MacBook M1 Pro
model_path = "models/chat/mistral-7b-instruct-v0.1.Q3_K_M.gguf"

llm = AutoModelForCausalLM.from_pretrained(
    model_path,
    model_type="mistral",
    gpu_layers=0,  # Set ke 0 karena MacBook M1 Pro tidak punya GPU CUDA
    context_length=2048,  # Optimasi untuk penggunaan memori rendah
    temperature=0.7
)

def generate_response(prompt: str) -> str:
    """Fungsi untuk menghasilkan respons dari LLM."""
    response = llm(prompt)
    return response
