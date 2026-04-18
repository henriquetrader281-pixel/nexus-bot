import streamlit as st
from groq import Groq
import urllib.parse

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        ID_AFILIADO = "18316451024"
        
        # A estrutura oficial da Shopee para busca com tracking de afiliado (smtt)
        # O smtt=0.0.ID é o padrão ouro para fixar a comissão no clique
        urls_base = {
            "Shopee": f"https://shopee.com.br/search?smtt=0.0.{ID_AFILIADO}&keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(marketplace, f"https://shopee.com.br/search?smtt=0.0.{ID_AFILIADO}&keyword=")

        if "AIDA" not in prompt.upper():
            prompt += f"""
            \nREGRAS DE OURO:
            - Formato por linha: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_do_produto] ###
            - No campo URL, substitua espaços por %20 para o link não quebrar.
            """

        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um terminal de extração de dados. Responda apenas com a lista bruta separada por ###."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return chat.choices[0].message.content.replace("**", "").strip()
    except Exception as e:
        return f"Erro: {str(e)}"
