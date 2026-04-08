import streamlit as st
from groq import Groq
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # --- ROTA DE INTELIGÊNCIA (Arsenal/Estúdio/Copy) ---
    if any(k in nicho for k in ["AIDA", "Copywriter", "Ignore", "###", "Roteiro"]):
        try:
       # Dentro do mineracao.py
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"],
    transport='rest' # 🚀 Isso aqui mata o erro 404
)
model = genai.GenerativeModel('gemini-1.5-flash')
            )
            
            # Tentamos o Flash, que é o mais resiliente a erros 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(nicho)
            return response.text
            
        except Exception as e:
            # Se o Flash falhar, ele tenta o Pro como última alternativa
            try:
                model_pro = genai.GenerativeModel('gemini-1.5-pro')
                return model_pro.generate_content(nicho).text
            except:
                return f"Erro Crítico Gemini: {str(e)}"
    
    # --- ROTA DE VARREDURA (Scanner) via Groq ---
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Aja como minerador. Liste {qtd} produtos de {nicho}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: https://shopee.com.br/search?keyword=[nome]"

            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq: {str(e)}"
