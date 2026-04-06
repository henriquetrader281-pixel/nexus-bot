import streamlit as st
from groq import Groq

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Chama a IA para minerar produtos com base nos parâmetros.
    """
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = f"""
    Aja como um especialista em E-commerce. 
    Liste 10 produtos virais de {nicho} para vender no {mkt_alvo}.
    
    USE EXATAMENTE ESTE FORMATO PARA CADA PRODUTO:
    NOME: [nome] | CALOR: [0-100] | VALOR: [preço] | TICKET: [baixo/médio] | URL: [link]
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na mineração: {str(e)}"

# ESTA FUNÇÃO TEM QUE ESTAR FORA (SEM ESPAÇOS NO INÍCIO DA LINHA)
def formatar_saida_limpa(texto_bruto):
    """
    Limpa o texto para o Scanner do app.py conseguir ler.
    """
    if not texto_bruto:
        return ""
    
    # Remove negritos e limpa espaços
    limpo = texto_bruto.replace("**", "").replace("Aqui está a lista:", "").strip()
    
    # Garante que comece no primeiro produto
    if "NOME:" in limpo:
        pos = limpo.find("NOME:")
        limpo = limpo[pos:]
        
    return limpo
