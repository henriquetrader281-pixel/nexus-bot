import streamlit as st
from groq import Groq
import re
import random

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: API Key faltando."
        
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # PROMPT ATUALIZADO: Solicita 30 produtos (10 de cada ticket)
    prompt = f"""
    Aja como um analista de tendências da Shopee {mkt_alvo}.
    Liste 30 produtos virais para o nicho: {nicho}.
    
    ESTRUTURA DA RESPOSTA:
    - 10 produtos de TICKET: Baixo
    - 10 produtos de TICKET: Médio
    - 10 produtos de TICKET: Alto
    
    FORMATO OBRIGATÓRIO POR LINHA (SEM COMENTÁRIOS):
    NOME: [nome] | CALOR: [número entre 70 e 98] | VALOR: [preço] | TICKET: [Baixo/Médio/Alto] | URL: [link]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3 # Aumentado levemente para aguentar 30 itens sem repetir muito
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto: return ""
    
    # 1. Remove lixo visual
    limpo = texto_bruto.replace("**", "").replace("###", "")
    
    # 2. Força quebra de linha em cada produto
    limpo = re.sub(r'(?i)NOME:', r'\nNOME:', limpo)
    
    linhas = limpo.split('\n')
    linhas_finais = []
    
    for l in linhas:
        if "|" in l and "NOME:" in l.upper():
            linha_processada = l.strip()
            
            # --- TRAVA DE SEGURANÇA PARA O CALOR ---
            # Se a IA mandar 250 graus, o código abaixo corrige para um valor real (80-98)
            try:
                match_calor = re.search(r'CALOR:\s*(\d+)', linha_processada.upper())
                if match_calor:
                    valor_calor = int(match_calor.group(1))
                    if valor_calor > 100:
                        novo_calor = random.randint(85, 98)
                        linha_processada = re.sub(r'CALOR:\s*\d+', f'CALOR: {novo_calor}', linha_processada, flags=re.IGNORECASE)
            except:
                pass
                
            linhas_finais.append(linha_processada)
            
    return "\n".join(linhas_finais)
