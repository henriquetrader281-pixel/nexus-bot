import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Base de busca para o link (como estava no seu script original)
        urls_base = {
            "Shopee": "https://shopee.com.br/search?keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(marketplace, "https://shopee.com.br/search?keyword=")

        # Forçamos a IA a usar URL em vez de LINK
        if "###" not in prompt: # Se não for copy
            prompt += f"\nResponda APENAS no formato: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome] ###"

        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"
