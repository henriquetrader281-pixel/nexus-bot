import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Base de busca (O segredo da versão que funcionava)
        urls_base = {
            "Shopee": "https://shopee.com.br/search?keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(marketplace, "https://shopee.com.br/search?keyword=")
        id_afiliado = "18316451024"

        # Se for mineração (Scanner), forçamos o formato bruto
        if "###" not in prompt:
            prompt += f"\nResponda APENAS no formato: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]&smtt=0.0.{id_afiliado} ###"

        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um terminal de dados bruto. Não use saudações. Use ### para separar produtos."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        resposta = chat.choices[0].message.content
        # Limpeza para garantir que o app receba apenas a lista
        if "NOME:" in resposta.upper():
            return resposta[resposta.upper().find("NOME:"):]
        return resposta
    except Exception as e:
        return f"Erro: {str(e)}"
