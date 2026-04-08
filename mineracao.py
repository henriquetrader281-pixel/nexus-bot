import streamlit as st
import re
import random
import google.generativeai as genai

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # 1. BUSCA A CHAVE NOVA NOS SECRETS
    chave = st.secrets.get("GEMINI_API_KEY")
    if not chave:
        return "Erro: Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit."

    try:
        # 2. CONFIGURAÇÃO DA CHAVE
        genai.configure(api_key=chave)
        
        # 3. MATANDO O ERRO 404: 
        # Usamos o nome de modelo que o Google exige para contas estáveis/Plus
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        urls_base = {
            "Shopee": "https://shopee.com.br/search?keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

        prompt = f"""Liste {qtd} produtos virais de '{nicho}' para {mkt_alvo}.
        Use RIGOROSAMENTE este formato:
        NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"""
        
        # 4. DISPARO
        response = model.generate_content(prompt)
        
        # Validação extra para garantir que recebemos texto
        if response and response.text:
            return response.text
        else:
            return "Erro: A IA respondeu, mas o conteúdo veio vazio. Tente novamente."

    except Exception as e:
        # Se o 'flash-latest' falhar, tentamos a última cartada: o nome puro
        try:
            model_backup = genai.GenerativeModel('gemini-1.5-flash')
            response_backup = model_backup.generate_content(prompt)
            return response_backup.text
        except:
            return f"Erro na conexão Gemini (Plus/Estável): {str(e)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto: return ""
    limpo = texto_bruto.replace("**", "").strip()
    # Pega apenas as linhas que seguem o formato Nexus
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
