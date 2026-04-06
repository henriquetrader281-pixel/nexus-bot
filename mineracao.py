import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor Nexus - Gera a lista garantindo que cada produto esteja em sua própria linha.
    """
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: Chave API GROQ_API_KEY não encontrada nos Secrets."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = f"""
    Aja como um minerador de produtos virais da Shopee Brasil.
    Liste 10 produtos para o nicho {nicho}.
    
    REGRAS CRÍTICAS:
    1. Escreva UM produto por linha.
    2. Use EXATAMENTE este formato:
    NOME: [nome] | CALOR: [80-99] | VALOR: [preço] | TICKET: [Baixo/Médio/Alto] | URL: https://shopee.com.br
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
    Limpa o texto e FORÇA a quebra de linha onde houver a palavra 'NOME:'
    Isso corrige o erro de aparecer tudo grudado.
    """
    if not texto_bruto:
        return ""
    
    # Remove asteriscos e lixo
    texto = texto_bruto.replace("**", "").replace("#", "").strip()
    
    # FORÇA uma quebra de linha antes de cada 'NOME:' caso a IA mande tudo grudado
    texto = texto.replace("NOME:", "\nNOME:")
    
    linhas = texto.split('\n')
    linhas_finais = []
    
    for linha in linhas:
        if "|" in linha and "NOME:" in linha.upper():
            l = linha.strip()
            
            # Adiciona [SHOPEE] se não tiver
            if "[SHOPEE]" not in l.upper():
                l = l.replace("NOME:", "NOME: [SHOPEE]")
            
            # Garante que o TICKET exista para o seletor não bugar
            if "TICKET:" not in l.upper():
                l = l.replace("| URL:", "| TICKET: Médio | URL:")
                
            linhas_finais.append(l)
            
    return "\n".join(linhas_finais)
