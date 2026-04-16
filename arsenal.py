import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    """Motor Groq de Alta Velocidade para Scan e Copy"""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Define se é criativo (Copy) ou preciso (Lista de Produtos)
        is_copy = any(k in prompt for k in ["AIDA", "Copywriter", "###", "Roteiro", "Estratégia"])
        temp = 0.7 if is_copy else 0.2
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=temp
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Erro Crítico Groq: {str(e)}"
