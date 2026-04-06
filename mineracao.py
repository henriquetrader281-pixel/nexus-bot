import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    prompt = f"Liste 10 produtos de {nicho} para Shopee {mkt_alvo}. Formato: NOME: [n] | CALOR: [c] | VALOR: [v] | TICKET: [t] | URL: [u]. UM POR LINHA."
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return ""

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto: return ""
    
    # LIMPEZA TOTAL: Remove asteriscos e força quebra de linha antes de 'NOME:'
    limpo = texto_bruto.replace("**", "").replace("###", "")
    limpo = re.sub(r'(?i)NOME:', r'\nNOME:', limpo) # Aqui mata o erro do texto grudado
    
    linhas = limpo.split('\n')
    return "\n".join([l.strip() for l in linhas if "|" in l])
