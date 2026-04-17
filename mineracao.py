import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # ID Fixo para o rastro do afiliado
        ID_AFILIADO = "18316451024"
        
        # Bases de busca com suporte a rastreio (smtt para Shopee)
        urls_base = {
            "Shopee": "https://shopee.com.br/search?smtt=0.0." + ID_AFILIADO + "&keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(marketplace, "https://shopee.com.br/search?keyword=")

        # Refinamos o prompt para a IA não colocar espaços nem asteriscos nos links
        if "AIDA" not in prompt.upper() and "COPY" not in prompt.upper():
            prompt += f"""
            \nREGRAS DE OURO:
            1. Use o separador ### entre produtos.
            2. No campo URL, substitua espaços por %20.
            3. Formato EXATO: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_sem_espacos] ###
            """

        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um terminal de dados bruto. Não use markdown (**). Responda apenas com a lista de produtos separada por ###."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1 
        )
        
        resposta = chat.choices[0].message.content
        
        # LIMPEZA DE ELITE: Remove asteriscos que a IA insiste em colocar e que quebram o link
        return resposta.replace("**", "").replace("`", "").strip()

    except Exception as e:
        return f"Erro na Groq: {str(e)}"
