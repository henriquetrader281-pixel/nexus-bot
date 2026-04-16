import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Identifica se é Copy ou Varredura pelo conteúdo do prompt
    is_copy = any(k in prompt for k in ["AIDA", "Copywriter", "###", "Roteiro", "Estratégia"])
    
    try:
        # Temperatura: 0.7 para criatividade (Copy) | 0.2 para precisão (Scanner)
        temp = 0.7 if is_copy else 0.2
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=temp
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Erro Groq: {str(e)}"
