import streamlit as st
import requests

st.title("🤖 AI Assistant - Mistral Chatbot")

user_input = st.text_area("Masukkan pertanyaan:")

if st.button("Kirim"):
    if user_input:
        response = requests.post("http://127.0.0.1:8000/chat/", json={"prompt": user_input})
        bot_response = response.json()["response"]
        st.write("🧠 Jawaban AI:")
        st.write(bot_response)
    else:
        st.warning("Silakan masukkan pertanyaan terlebih dahulu.")
