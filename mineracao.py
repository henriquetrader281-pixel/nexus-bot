import streamlit as st
from groq import Groq

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor de Mineração Nexus - Força a inclusão do TICKET
    """
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = f"""
    Aja como um analista de E-commerce. Liste 10 produtos virais de {nicho} na {mkt_alvo}.
    
    IMPORTANTE: Retorne CADA produto EXATAMENTE neste formato de uma única linha:
    NOME: [nome] | CALOR: [0-100] | VALOR: [R$] | TICKET: [Baixo ou Médio ou Alto] | URL: [link]
    
    Regra de Ticket: Até R$80 é Baixo, R$80-R$250 é Médio, acima é Alto.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1 # Temperatura baixa para não errar o formato
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Tratamento de erro para campos vazios ou formatos errados
    """
    if not texto_bruto:
        return ""
    
    linhas = texto_bruto.split('\n')
    linhas_final = []
    
    for linha in linhas:
        if "|" in linha and "NOME:" in linha:
            l = linha.replace("**", "").strip()
            
            # Se a IA esqueceu o TICKET, vamos tentar adivinhar pelo valor ou injetar "Médio"
            if "TICKET:" not in l:
                l = l.replace("| URL:", "| TICKET: Médio | URL:")
            
            # Garante a tag da Shopee para o utilizador ver
            if "shopee" not in l.lower():
                l = l.replace("NOME:", "NOME: [SHOPEE]")
                
            linhas_final.append(l)
            
    return "\n".join(linhas_final)
