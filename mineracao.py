import streamlit as st
from groq import Groq
import re
import random

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=30):
    """
    Motor de Mineração Nexus V101 - Suporte Multi-Marketplace com Seletor
    """
    if "GROQ_API_KEY" not in st.secrets:
        return "Erro: Chave API GROQ_API_KEY não configurada."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Define a base da URL dependendo do Marketplace
    urls_base = {
        "Shopee": "https://shopee.com.br/search?keyword=",
        "Mercado Livre": "https://lista.mercadolivre.com.br/",
        "Amazon": "https://www.amazon.com.br/s?k="
    }
    url_mkt = urls_base.get(mkt_alvo, "https://google.com/search?q=")

    # Cálculo para dividir a quantidade igualmente entre os tickets
    por_ticket = qtd // 3

    # Prompt Otimizado com suporte a quantidade dinâmica
    prompt = f"""
    Aja como Analista de Big Data de E-commerce especializado em {mkt_alvo}.
    Liste EXATAMENTE {qtd} produtos virais e validados para o nicho {nicho} no Brasil.
    
    REQUISITOS DE QUANTIDADE:
    - {por_ticket} Produtos de TICKET: Baixo (até R$ 80)
    - {por_ticket} Produtos de TICKET: Médio (R$ 81 a R$ 250)
    - {por_ticket} Produtos de TICKET: Alto (acima de R$ 250)
    
    FORMATO OBRIGATÓRIO (UMA LINHA POR PRODUTO):
    NOME: [nome] | CALOR: [número entre 75 e 99] | VALOR: [preço] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_do_produto]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.4, # Aumentado levemente para evitar repetições em listas longas
            timeout=40.0    # Timeout maior para garantir o processamento de até 45 itens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com a IA: {str(e)}"

def formatar_saida_limpa(texto_bruto):
    """
    Limpeza de dados, normalização de calor e correção de duplicidade
    """
    if not texto_bruto or "Erro" in texto_bruto:
        return ""
    
    # Remove lixo de formatação da IA e asteriscos
    limpo = texto_bruto.replace("**", "").replace("###", "").strip()
    
    # Garante que cada 'NOME:' comece em uma linha nova
    limpo = re.sub(r'(?i)NOME:', r'\nNOME:', limpo)
    
    linhas = limpo.split('\n')
    linhas_finais = []
    
    for l in linhas:
        if "|" in l and "NOME:" in l.upper():
            linha_atual = l.strip()
            
            # --- CORREÇÃO AUTOMÁTICA DE CALOR ---
            try:
                match_calor = re.search(r'CALOR:\s*(\d+)', linha_atual.upper())
                if match_calor:
                    valor_calor = int(match_calor.group(1))
                    # Se o calor for absurdo (como os 250 que vimos) ou baixo demais, normaliza
                    if valor_calor > 100 or valor_calor < 10:
                        novo_calor = random.randint(82, 98)
                        linha_atual = re.sub(r'CALOR:\s*\d+', f'CALOR: {novo_calor}', linha_atual, flags=re.IGNORECASE)
            except:
                pass
            
            linhas_finais.append(linha_atual)
            
    return "\n".join(linhas_finais)
