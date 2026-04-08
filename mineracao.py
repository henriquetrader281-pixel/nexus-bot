import streamlit as st
from groq import Groq
import re
import random

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    """
    Motor Híbrido: Mineração via Groq (Llama 3) para máxima velocidade.
    """
    # 1. BUSCA A CHAVE DA GROQ NOS SECRETS
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: Chave GROQ_API_KEY não configurada nos Secrets."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Define a base da URL dependendo do Marketplace
    urls_base = {
        "Shopee": "https://shopee.com.br/search?keyword=",
        "Mercado Livre": "https://lista.mercadolivre.com.br/",
        "Amazon": "https://www.amazon.com.br/s?k="
    }
    url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

    # Cálculo para dividir a quantidade igualmente
    por_ticket = qtd // 3

    # Prompt Otimizado para a Groq ser cirúrgica
    prompt = f"""
    Aja como Analista de Big Data de E-commerce especializado em {mkt_alvo}.
    Liste EXATAMENTE {qtd} produtos virais para o nicho {nicho} no Brasil.
    
    FORMATO OBRIGATÓRIO (UMA LINHA POR PRODUTO):
    NOME: [nome] | CALOR: [número entre 75 e 99] | VALOR: R$ [preço] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_do_produto]
    """
    
    try:
        # Aqui ele volta a usar o Llama-3 que é instantâneo para listas
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            timeout=25.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na mineração via Groq: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto:
        return ""
    
    limpo = texto_bruto.replace("**", "").replace("###", "").strip()
    limpo = re.sub(r'(?i)NOME:', r'\nNOME:', limpo)
    
    linhas = limpo.split('\n')
    linhas_finais = []
    
    for l in linhas:
        if "|" in l and "NOME:" in l.upper():
            linha_atual = l.strip()
            
            # Correção de Calor para manter o padrão Nexus
            try:
                match_calor = re.search(r'CALOR:\s*(\d+)', linha_atual.upper())
                if match_calor:
                    valor_calor = int(match_calor.group(1))
                    if valor_calor > 100 or valor_calor < 10:
                        novo_calor = random.randint(82, 98)
                        linha_atual = re.sub(r'CALOR:\s*\d+', f'CALOR: {novo_calor}', linha_atual, flags=re.IGNORECASE)
            except:
                pass
            
            linhas_finais.append(linha_atual)
            
    return "\n".join(linhas_finais)
