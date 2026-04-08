import streamlit as st
from groq import Groq
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # --- ROTA DE INTELIGÊNCIA (Arsenal/Estúdio/Copy) via Gemini Plus ---
    # O gatilho agora é a presença de "AIDA" ou regras vindas do copy.py
    if any(k in nicho for k in ["AIDA", "Copywriter", "Ignore", "###"]):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # 🔱 O PULO DO GATO: Forçamos a versão 'v1' (Estável)
            opcoes = RequestOptions(api_version="v1")
            model = genai.GenerativeModel('gemini-1.5-pro') 
            
            response = model.generate_content(nicho, request_options=opcoes)
            return response.text
        except Exception as e:
            return f"Erro Crítico Gemini: {str(e)}"
    
    # --- ROTA DE VARREDURA (Scanner) via Groq ---
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
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

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto: return ""
    limpo = texto_bruto.replace("**", "").strip()
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
