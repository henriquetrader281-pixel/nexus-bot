import streamlit as st
from groq import Groq

def minerar_produtos(nicho, mkt_alvo, motor_ia):
    """
    Motor de Mineração Nexus - Força o formato correto para o Scanner
    """
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # O segredo está neste prompt detalhado
    prompt = f"""
    Aja como um analista de tendências da {mkt_alvo} Brasil.
    Liste 10 produtos de alto volume de vendas para o nicho: {nicho}.
    
    Para cada produto, retorne EXATAMENTE nesta linha (sem asteriscos):
    NOME: [nome do produto] | CALOR: [número de 0 a 100] | VALOR: [preço em R$] | TICKET: [Baixo/Médio] | URL: [link shopee]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2 # Menos criatividade = mais precisão no formato
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Transforma o texto da IA em algo que o Scanner entende perfeitamente.
    """
    if not texto_bruto:
        return ""
    
    # Remove qualquer lixo que a IA mande antes ou depois
    linhas = texto_bruto.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        if "NOME:" in linha and "|" in linha:
            # Limpa símbolos de negrito e espaços extras
            l = linha.replace("**", "").replace("###", "").strip()
            # Garante que a tag do marketplace apareça no nome se não existir
            if "shopee" in l.lower() or "Shopee" in l:
                linhas_limpas.append(l)
            else:
                linhas_limpas.append(l.replace("NOME:", "NOME: [SHOPEE]"))
                
    return "\n".join(linhas_limpas)
    
