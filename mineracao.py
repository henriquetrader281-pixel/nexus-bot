import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia): # Adicione o _ aqui
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Tudo o que estiver abaixo também precisa de 4 espaços de recuo
    if any(k in nicho for k in ["AIDA", "Copywriter", "###", "Roteiro"]):
        try:
            # Continuação do código...
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
