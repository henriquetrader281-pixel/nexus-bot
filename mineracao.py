import streamlit as st
import re
import random
import google.generativeai as genai
from google.generativeai.types import RequestOptions

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    # 1. BUSCA A CHAVE NOS SECRETS
    chave = st.secrets.get("GEMINI_API_KEY")
    if not chave:
        return "Erro: Chave 'GEMINI_API_KEY' não encontrada nos Secrets."

    try:
        # 2. CONFIGURAÇÃO COM FORÇA BRUTA NA VERSÃO V1 (ESTÁVEL)
        genai.configure(api_key=chave)
        
        # Criamos uma configuração de rota para ignorar a v1beta que está dando erro
        opcoes = RequestOptions(api_version="v1")
        
        # 3. DEFINIÇÃO DO MODELO ESTÁVEL
        # Usamos o flash-8b ou flash por ser o mais compatível com chaves novas
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        urls_base = {
            "Shopee": "https://shopee.com.br/search?keyword=",
            "Mercado Livre": "https://lista.mercadolivre.com.br/",
            "Amazon": "https://www.amazon.com.br/s?k="
        }
        url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

        prompt = f"""Atue como minerador de produtos virais. Nicho: {nicho}. Marketplace: {mkt_alvo}.
        Liste {qtd} produtos. Use EXATAMENTE este formato por linha:
        NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"""
        
        # 4. DISPARO FORÇANDO A ROTA V1
        response = model.generate_content(prompt, request_options=opcoes)
        
        if response.text:
            return response.text
        else:
            return "Erro: Resposta vazia da IA."

    except Exception as e:
        # Se falhar, tentamos a última rota possível sem prefixos
        try:
            model_alt = genai.GenerativeModel('gemini-1.5-pro')
            res_alt = model_alt.generate_content(prompt, request_options=RequestOptions(api_version="v1"))
            return res_alt.text
        except Exception as e2:
            return f"Erro Crítico de Conexão (v1): {str(e2)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto: return ""
    limpo = texto_bruto.replace("**", "").strip()
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
