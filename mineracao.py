import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor Nexus V2 - Ultra Estrito para evitar 'Desconhecido'
    """
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: Chave API não configurada."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Prompt simplificado para evitar que a IA invente moda
    prompt = f"""
    Liste 10 produtos virais de {nicho} na Shopee {mkt_alvo}.
    Responda APENAS linhas seguindo este modelo exato, sem mais nada:
    NOME: Nome do Produto | CALOR: 85 | VALOR: 49.90 | TICKET: Baixo | URL: https://shopee.com.br
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na API: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Limpeza Profunda: Remove asteriscos e garante que o app leia os campos.
    """
    if not texto_bruto: return ""
    
    # 1. Remove qualquer asterisco (*) ou hashtag (#) que a IA teime em usar
    texto_limpo = texto_bruto.replace("*", "").replace("#", "")
    
    linhas = texto_limpo.split('\n')
    linhas_finais = []
    
    for linha in linhas:
        # Só aceita a linha se tiver o separador '|' e o campo 'NOME:'
        if "|" in linha and "NOME:" in linha.upper():
            l = linha.strip()
            
            # Força o nome a ter [SHOPEE] para não ficar vazio
            if "NOME:" in l.upper() and "[SHOPEE]" not in l.upper():
                l = l.replace("NOME:", "NOME: [SHOPEE] ")
            
            # Se faltar o TICKET, calcula pelo VALOR
            if "TICKET:" not in l.upper():
                valor_match = re.search(r'VALOR:\s*([\d.,]+)', l.upper())
                ticket = "Médio"
                if valor_match:
                    try:
                        v = float(valor_match.group(1).replace(',', '.'))
                        ticket = "Baixo" if v < 80 else "Médio" if v < 250 else "Alto"
                    except: pass
                l = l.replace("| URL:", f"| TICKET: {ticket} | URL:")
                
            linhas_finais.append(l)
            
    return "\n".join(linhas_finais)
