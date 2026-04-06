import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor Nexus - Gera a lista garantindo separação absoluta por linha.
    """
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: Chave API GROQ_API_KEY não encontrada nos Secrets."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Prompt "Doutrinador": obriga a IA a não usar parágrafos
    prompt = f"""
    Liste 10 produtos virais de {nicho} na Shopee {mkt_alvo}.
    Responda APENAS as linhas de dados. NÃO escreva introdução.
    
    FORMATO OBRIGATÓRIO (COPIE EXATAMENTE):
    NOME: [nome] | CALOR: [80-99] | VALOR: [preço] | TICKET: [Baixo/Médio/Alto] | URL: https://shopee.com.br
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1 # Mantém a IA focada e rígida
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na API: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Limpeza Extrema: Quebra o texto grudado e remove símbolos que causam 'Desconhecido'
    """
    if not texto_bruto:
        return ""
    
    # 1. Remove asteriscos e marcações que a IA coloca e quebram o split do app.py
    texto = texto_bruto.replace("**", "").replace("###", "").replace("- NOME:", "NOME:")
    
    # 2. CORREÇÃO DO TEXTO GRUDADO: Força uma nova linha antes de cada 'NOME:'
    # Isso resolve o que você viu no seu print do Arsenal.
    texto = re.sub(r'(?i)NOME:', r'\nNOME:', texto)
    
    linhas = texto.split('\n')
    linhas_finais = []
    
    for linha in linhas:
        # Só processa se a linha tiver os dados básicos
        if "|" in linha and "NOME:" in linha.upper():
            l = linha.strip()
            
            # Garante que o nome contenha [SHOPEE] para o Scanner identificar
            if "[SHOPEE]" not in l.upper():
                l = l.replace("NOME:", "NOME: [SHOPEE]")
            
            # Se a IA esqueceu o Ticket no texto grudado, nós injetamos
            if "TICKET:" not in l.upper():
                l = l.replace("| URL:", "| TICKET: Médio | URL:")
                
            linhas_finais.append(l)
            
    # Retorna as linhas separadas corretamente por \n
    return "\n".join(linhas_finais)
