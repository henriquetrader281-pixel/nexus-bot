import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    # Inicializa o cliente Groq usando a chave dos Secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Identifica se a rota é para Copy (Arsenal) ou Listagem (Scanner)
    # Se o prompt tiver gatilhos de copy, aumenta a temperatura (criatividade)
    is_copy = any(k in prompt for k in ["AIDA", "Copywriter", "###", "Roteiro", "Estratégia"])
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7 if is_copy else 0.2
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Erro Groq: {str(e)}"
