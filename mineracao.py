import streamlit as st
import re
import random
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # 1. BUSCA A CHAVE NOVA NOS SECRETS
    chave = st.secrets.get("GEMINI_API_KEY")
    if not chave:
        return "Erro: Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit."

    try:
        # 2. CONFIGURAÇÃO DA CHAVE
        genai.configure(api_key=chave)
        
        # 3. MODELO FLASH (O mais estável para chaves novas)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        urls_base = {
            "Shopee": "https://shopee.com.br/search?keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

        prompt = f"""Liste {qtd} produtos virais de '{nicho}' para {mkt_alvo}.
        Use RIGOROSAMENTE este formato:
        NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"""
        
        # 4. DISPARO
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Erro detalhado para sabermos se o problema é a chave ou a cota
        return f"Erro na conexão Gemini: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto: return ""
    limpo = texto_bruto.replace("**", "").strip()
    # Pega apenas as linhas que seguem o formato Nexus
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
