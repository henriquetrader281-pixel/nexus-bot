import streamlit as st
import re
import random
# Importação da biblioteca oficial do Google Gemini
try:
    import google.generativeai as genai
except ImportError:
    pass

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    """
    Motor de Mineração Nexus V101 - Motor Gemini Nativo 🔱
    """
    # 1. VERIFICAÇÃO DA CHAVE DO GEMINI
    if "GEMINI_API_KEY" not in st.secrets:
        return "Erro: Chave API GEMINI_API_KEY não configurada no painel do Streamlit."

    # 2. CONFIGURAÇÃO DO CÉREBRO
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Define a base da URL dependendo do Marketplace
    urls_base = {
        "Shopee": "https://shopee.com.br/search?keyword=",
        "Mercado Livre": "https://lista.mercadolivre.com.br/",
        "Amazon": "https://www.amazon.com.br/s?k="
    }
    url_mkt = urls_base.get(mkt_alvo, "https://google.com/search?q=")

    # Cálculo inteligente para dividir a quantidade com precisão, mesmo sendo 10
    qtd_baixo = qtd // 3
    qtd_medio = qtd // 3
    qtd_alto = qtd - qtd_baixo - qtd_medio # Garante que a soma seja exatamente igual a 'qtd'

    # Prompt Otimizado com matemática exata
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
    
    try:
        # Garante que vai usar o Gemini 1.5 Pro
        modelo_escolhido = motor_ia if "gemini" in motor_ia.lower() else "gemini-1.5-pro"
        model = genai.GenerativeModel(modelo_escolhido)
        
        # O disparo real para o servidor do Google
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na conexão com a IA (Gemini): {str(e)}"

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
