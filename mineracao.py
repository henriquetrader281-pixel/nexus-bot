import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor de Mineração Nexus - Ultra Estrito
    """
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = f"""
    Aja como um analista de E-commerce. Liste 10 produtos virais de {nicho} na {mkt_alvo}.
    
    FORMATO OBRIGATÓRIO (UMA LINHA POR PRODUTO):
    NOME: [nome] | CALOR: [0-100] | VALOR: [R$] | TICKET: [Baixo/Médio/Alto] | URL: [link]
    
    REGRAS:
    1. Use 'Baixo' para valores até R$ 80.
    2. Use 'Médio' para R$ 81 até R$ 250.
    3. Use 'Alto' para acima de R$ 250.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Limpeza Inteligente: Se o Ticket faltar, o código calcula e insere.
    """
    if not texto_bruto:
        return ""
    
    linhas = texto_bruto.split('\n')
    linhas_finais = []
    
    for linha in linhas:
        if "NOME:" in linha and "|" in linha:
            # Limpeza básica de asteriscos e espaços
            l = linha.replace("**", "").replace("###", "").strip()
            
            # --- CORREÇÃO AUTOMÁTICA DE TICKET ---
            if "TICKET:" not in l.upper():
                # Tenta extrair o valor numérico para definir o ticket manualmente
                valor_match = re.search(r'VALOR:\s*[R$\s]*([\d.,]+)', l.upper())
                if valor_match:
                    try:
                        valor_num = float(valor_match.group(1).replace('.', '').replace(',', '.'))
                        if valor_num <= 80: ticket = "Baixo"
                        elif valor_num <= 250: ticket = "Médio"
                        else: ticket = "Alto"
                    except:
                        ticket = "Médio"
                else:
                    ticket = "Médio"
                
                # Injeta o Ticket antes da URL
                l = l.replace("| URL:", f"| TICKET: {ticket} | URL:")
            
            # --- GARANTIA DA SHOPEE ---
            if "SHOPEE" not in l.upper():
                l = l.replace("NOME:", "NOME: [SHOPEE]")
                
            linhas_finais.append(l)
            
    return "\n".join(linhas_finais)
