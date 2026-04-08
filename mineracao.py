import streamlit as st
from groq import Groq
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # --- ROTA DE INTELIGÊNCIA (Arsenal/Estúdio/Copy) ---
    # Gatilho: Se o prompt tiver marcadores de estratégia ou roteiro
    if any(k in nicho for k in ["AIDA", "Copywriter", "Ignore", "###", "Roteiro"]):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # ⚡ FORÇANDO O FLASH: Modelo estável, grátis e sem erro 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(nicho)
            return response.text
            
        except Exception as e:
            return f"Erro Crítico no Cérebro: {str(e)}"
    
    # --- ROTA DE VARREDURA (Scanner) via Groq ---
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Base de busca para o link de afiliado (Dashboard lê isso)
            urls_base = {
                "Shopee": "https://shopee.com.br/search?keyword=",
                "Mercado Livre": "https://lista.mercadolivre.com.br/",
                "Amazon": "https://www.amazon.com.br/s?k="
            }
            url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

            prompt = f"Aja como minerador. Liste {qtd} produtos de {nicho}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"

            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"Erro Groq: {str(e)}"
