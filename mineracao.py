import streamlit as st
from groq import Groq
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # --- ROTA DE INTELIGÊNCIA (Arsenal/Estúdio) ---
    if any(k in nicho for k in ["AIDA", "Copywriter", "Ignore", "###", "Roteiro"]):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # Em 2026, usamos o modelo com o sufixo mais estável
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(nicho)
            return response.text
        except Exception as e:
            # Fallback para o Flash se o Pro der 404
            try:
                model_fb = genai.GenerativeModel('gemini-1.5-flash')
                return model_fb.generate_content(nicho).text
            except:
                return f"Erro Gemini: {str(e)}"
    
    # --- ROTA SCANNER (Groq) ---
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
