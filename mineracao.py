import streamlit as st
import re
import random
try:
    import google.generativeai as genai
except ImportError:
    pass

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    """
    Motor de Mineração Nexus V101 - Edição Gemini Plus (Rota Fixa) 🔱
    """
    if "GEMINI_API_KEY" not in st.secrets:
        return "Erro: GEMINI_API_KEY não encontrada nos Secrets."

    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    urls_base = {
        "Shopee": "https://shopee.com.br/search?keyword=",
        "Mercado Livre": "https://lista.mercadolivre.com.br/",
        "Amazon": "https://www.amazon.com.br/s?k="
    }
    url_mkt = urls_base.get(mkt_alvo, "https://google.com/search?q=")

    qtd_baixo = qtd // 3
    qtd_medio = qtd // 3
    qtd_alto = qtd - qtd_baixo - qtd_medio

    prompt = f"""
    Aja como Analista de Big Data de E-commerce especializado em {mkt_alvo}.
    Liste EXATAMENTE {qtd} produtos virais e validados para o nicho {nicho} no Brasil.
    
    REQUISITOS DE QUANTIDADE (TOTAL DE {qtd}):
    - {qtd_baixo} Produtos de TICKET: Baixo (até R$ 80)
    - {qtd_medio} Produtos de TICKET: Médio (R$ 81 a R$ 250)
    - {qtd_alto} Produtos de TICKET: Alto (acima de R$ 250)
    
    FORMATO OBRIGATÓRIO (UMA LINHA POR PRODUTO):
    NOME: [nome] | CALOR: [número entre 75 e 99] | VALOR: [preço] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome_do_produto]
    """
    
    # Lista de modelos por ordem de potência para o seu plano Plus
    modelos_tentar = ["gemini-1.5-pro-002", "gemini-1.5-pro", "gemini-1.5-flash-002"]
    
    ultima_excecao = ""
    for nome_modelo in modelos_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            ultima_excecao = str(e)
            continue # Tenta o próximo modelo se o atual der 404
            
    return f"Erro Crítico de Rota no Gemini Plus: {ultima_excecao}"

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
            try:
                match_calor = re.search(r'CALOR:\s*(\d+)', linha_atual.upper())
                if match_calor:
                    valor_calor = int(match_calor.group(1))
                    if valor_calor > 100 or valor_calor < 10:
                        novo_calor = random.randint(82, 98)
                        linha_atual = re.sub(r'CALOR:\s*\d+', f'CALOR: {novo_calor}', linha_atual, flags=re.IGNORECASE)
            except: pass
            linhas_finais.append(linha_atual)
    return "\n".join(linhas_finais)
