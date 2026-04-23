import streamlit as st
from groq import Groq
import urllib.parse

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        ID_AFILIADO = "18316451024"
        
        # A MUDANÇA ESTÁ AQUI: Usamos o universal-link para garantir o clique no painel
        urls_base = {
            "Shopee": f"https://shopee.com.br/universal-link/search?smtt=0.0.{ID_AFILIADO}&keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(marketplace, f"https://shopee.com.br/universal-link/search?smtt=0.0.{ID_AFILIADO}&keyword=")

        if "AIDA" not in prompt.upper():
            prompt += f"""
            \nREGRAS DE OURO:
            - Formato por linha: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_do_produto]
            - No campo URL, substitua espaços por %20 e NUNCA adicione ### no final da URL para não quebrar o link.
            """

        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um terminal de extração de dados. Responda apenas com a lista bruta sem comentários."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        # Limpeza para garantir que o Streamlit leia o link puro
        resultado = chat.choices[0].message.content.replace("**", "").replace("###", "").strip()
        return resultado
    except Exception as e:
        return f"Erro: {str(e)}"
