import streamlit as st
from groq import Groq
import google.generativeai as genai
from openai import OpenAI # 🚀 Novo componente

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # --- ROTA DE INTELIGÊNCIA (Arsenal/Estúdio) ---
    if any(k in nicho for k in ["AIDA", "Copywriter", "Ignore", "###", "Roteiro"]):
        
        # 🤖 OPÇÃO A: USAR GPT (OpenAI)
        if motor_ia == "gpt-4o-mini":
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": nicho}],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Erro OpenAI: {str(e)}"

        # ♊ OPÇÃO B: USAR GEMINI (Google)
        else:
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                return model.generate_content(nicho).text
            except:
                # Fallback automático para o Flash se o Pro cair
                model_fb = genai.GenerativeModel('gemini-1.5-flash')
                return model_fb.generate_content(nicho).text
    
    # --- ROTA SCANNER (Groq) ---
    else:
        # (Mantém seu código atual do Groq aqui...)
        pass
