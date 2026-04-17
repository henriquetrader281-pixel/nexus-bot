import streamlit as st
from groq import Groq

@st.cache_data
def minerar_produtos(prompt, marketplace, _motor_ia):
    """
    Motor Groq Llama 3.3 Versatile - Otimizado para Nexus V101
    """
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Identifica o objetivo (Copy vs Scanner)
        is_copy = any(k in prompt.upper() for k in ["AIDA", "COPYWRITER", "###", "ROTEIRO", "ESTRATÉGIA"])
        
        # Se for Scanner, forçamos a IA a não "conversar"
        if not is_copy:
            prompt += "\nRETORNE APENAS OS DADOS. NÃO DIGA 'AQUI ESTÁ SUA LISTA'. USE O SEPARADOR ###"

        # Ajuste de Temperatura
        temp = 0.7 if is_copy else 0.1  # Baixei para 0.1 para o Scanner ser ultra-preciso
        
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um robô de mineração de dados. Responda apenas o que for solicitado de forma bruta."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temp,
            max_tokens=2000
        )
        
        resposta = chat.choices[0].message.content
        
        # LIMPEZA DE SEGURANÇA: Remove qualquer texto que venha antes de "NOME:"
        if "NOME:" in resposta.upper() and not is_copy:
            pos = resposta.upper().find("NOME:")
            return resposta[pos:]
            
        return resposta

    except Exception as e:
        return f"Erro Groq: {str(e)}"
