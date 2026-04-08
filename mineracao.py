import streamlit as st
from groq import Groq
import google.generativeai as genai
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # Se for pedido de COPY (Arsenal/Estúdio), usa Gemini Plus
    if "Ignore saudações" in nicho or "Aja como" in nicho:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(nicho)
            return response.text
        except Exception as e:
            return f"Erro Gemini: {str(e)}"
    
    # Se for MINERAÇÃO (Scanner), usa Groq para ser instantâneo
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Liste {qtd} produtos de {nicho} para {mkt_alvo}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [preço] | TICKET: [Baixo/Médio/Alto] | URL: https://shopee.com.br/search?keyword=[nome]"
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq: {str(e)}"
