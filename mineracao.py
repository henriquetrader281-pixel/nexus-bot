import streamlit as st
from groq import Groq
import re

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor de Mineração com Tratamento de Erros e Timeouts
    """
    # Verifica se a chave existe antes de tentar usar
    if "GROQ_API_KEY" not in st.secrets:
        return "❌ Erro: GROQ_API_KEY não configurada nos Secrets do Streamlit."

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        prompt = f"""
        Aja como um analista de E-commerce. Liste 10 produtos virais de {nicho} na {mkt_alvo}.
        
        FORMATO OBRIGATÓRIO (UMA LINHA POR PRODUTO):
        NOME: [nome] | CALOR: [0-100] | VALOR: [R$] | TICKET: [Baixo/Médio/Alto] | URL: [link shopee]
        
        Regras de Ticket: Baixo (até 80), Médio (81-250), Alto (acima de 250).
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            timeout=20.0 # Evita que o app fique travado para sempre
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ocorreu um erro na API: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Garante que o Scanner leia os dados mesmo com falhas da IA
    """
    if not texto_bruto or "Erro" in texto_bruto or "⚠️" in texto_bruto:
        return ""
    
    linhas = texto_bruto.split('\n')
    linhas_finais = []
    
    for linha in linhas:
        if "|" in linha and "NOME:" in linha:
            l = linha.replace("**", "").replace("###", "").strip()
            
            # Força o Ticket se ele não existir
            if "TICKET:" not in l.upper():
                l = l.replace("| URL:", "| TICKET: Médio | URL:")
            
            # Força o selo Shopee
            if "SHOPEE" not in l.upper():
                l = l.replace("NOME:", "NOME: [SHOPEE]")
                
            linhas_finais.append(l)
            
    return "\n".join(linhas_finais)
