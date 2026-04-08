import streamlit as st
from groq import Groq
import google.generativeai as genai
import re
import random

def minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=10):
    """
    Motor Híbrido Nexus:
    - Mineração (Scanner) -> Groq (Llama 3.3) - Ultra rápido
    - Estratégia (Arsenal/Estúdio) -> Gemini 1.5 Pro (Estável) - Inteligência Superior
    """
    
    # 🎯 IDENTIFICAÇÃO DE TAREFA: Se o prompt contém 'AIDA' ou 'Copy', vai para o Gemini
    if "AIDA" in nicho or "Copy" in nicho or "Ignore saudações" in nicho:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # 🛑 ROTA ESTÁVEL: Sem sufixos que causam 404
            model = genai.GenerativeModel('gemini-1.5-pro') 
            response = model.generate_content(nicho)
            return response.text
        except Exception as e:
            return f"Erro Gemini (Arsenal): {str(e)}"
    
    # 🔍 TAREFA DE MINERAÇÃO: Vai para a Groq
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Ajuste de URL para o Marketplace
            urls_base = {
                "Shopee": "https://shopee.com.br/search?keyword=",
                "Mercado Livre": "https://lista.mercadolivre.com.br/",
                "Amazon": "https://www.amazon.com.br/s?k="
            }
            url_mkt = urls_base.get(mkt_alvo, "https://shopee.com.br/search?keyword=")

            prompt = f"""Liste {qtd} produtos virais de {nicho} para {mkt_alvo}.
            Use RIGOROSAMENTE este formato por linha:
            NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: {url_mkt}[nome]"""

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Erro Groq (Scanner): {str(e)}"

def formatar_saida_limpa(texto_bruto):
    if not texto_bruto or "Erro" in texto_bruto:
        return ""
    # Limpa negritos e lixo de formatação
    limpo = texto_bruto.replace("**", "").replace("###", "").strip()
    linhas = [l.strip() for l in limpo.split('\n') if "|" in l and "NOME:" in l.upper()]
    return "\n".join(linhas)
