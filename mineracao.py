import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    # Inicializa o cliente Groq usando a chave dos Secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # --- FIX NameError: Define 'nicho' localmente para as verificações ---
    # Usamos o próprio conteúdo do prompt para identificar a rota
    conteudo_analise = prompt
    
    # 📝 ROTA DE COPY (Arsenal)
    # Se o prompt contiver palavras de copy, usa temperatura 0.7 (mais criativo)
    if any(k in conteudo_analise for k in ["AIDA", "Copywriter", "###", "Roteiro"]):
        try:
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7 
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq Copy: {str(e)}"
    
    # 🔍 ROTA DE VARREDURA (Scanner)
    # Se for lista de produtos, usa temperatura 0.2 (mais preciso e técnico)
    else:
        try:
            # Não precisamos de 'qtd' ou redefinir 'prompt' aqui, 
            # pois o 'prompt' que vem do app.py já está montado com volume e nicho.
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2 
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq Scanner: {str(e)}"
