import streamlit as st
import re
import random
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Erro: GEMINI_API_KEY ausente nos Secrets."

    # Configuração estável para plano Plus
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    urls_base = {
        "Shopee": "https://shopee.com.br/search?keyword=",
        "Mercado Livre": "https://lista.mercadolivre.com.br/",
        "Amazon": "https://www.amazon.com.br/s?k="
    }
    url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

    prompt = f"""Liste {qtd} produtos virais de '{nicho}' para {mkt_alvo}.
    Use RIGOROSAMENTE este formato:
    NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"""
    
    # Lista de modelos compatíveis com Gemini Plus (Ordem de tentativa)
    modelos = ["gemini-1.5-pro", "gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-1.5-flash"]
    
    for m in modelos:
        try:
            model = genai.GenerativeModel(model_name=m)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue
            
    return "Erro Crítico: O Google não reconheceu sua chave Plus. Verifique se a cota está ativa."

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto: return ""
    limpo = texto_bruto.replace("**", "").strip()
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
