import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Filtro de comportamento: Forçamos a IA a ser um terminal de dados
        is_copy = any(k in prompt.upper() for k in ["AIDA", "COPYWRITER", "###", "ROTEIRO"])
        
        system_msg = "Você é um banco de dados. Responda apenas com os dados solicitados. Proibido usar introduções ou conclusões."
        if not is_copy:
            prompt += "\nResponda apenas no formato: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url] ###"

        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Precisão máxima
            max_tokens=1500
        )
        
        res = chat.choices[0].message.content
        
        # LIMPEZA DE ELITE: Remove qualquer texto antes do primeiro 'NOME:'
        if "NOME:" in res.upper() and not is_copy:
            import re
            # Encontra a primeira ocorrência de NOME: ignorando maiúsculas/minúsculas
            match = re.search(r"NOME:", res, re.IGNORECASE)
            if match:
                res = res[match.start():]
        
        return res

    except Exception as e:
        return f"Erro Groq: {str(e)}"
