import streamlit as st
from groq import Groq

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # 🎯 ROTA DE COPY E ESTRATÉGIA (Arsenal e Estúdio)
    # Se o prompt for de marketing, usamos temperatura 0.7 para ser criativo
    if any(k in nicho for k in ["AIDA", "Copywriter", "###", "Roteiro"]):
        try:
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": nicho}],
                model="llama-3.3-70b-versatile",
                temperature=0.7 
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq Copy: {str(e)}"
    
    # 🔍 ROTA DE VARREDURA (Scanner)
    # Para listas, usamos temperatura 0.2 para ser preciso
    else:
        try:
            url_mkt = "https://shopee.com.br/search?keyword="
            prompt = f"Liste {qtd} produtos de {nicho}. Formato: NOME: [nome] | CALOR: [95] | VALOR: R$ [0,00] | TICKET: Baixo | URL: {url_mkt}[nome]"
            
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2 
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq Scanner: {str(e)}"
