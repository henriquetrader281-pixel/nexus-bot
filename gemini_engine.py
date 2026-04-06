import google.generativeai as genai
import streamlit as st

def configurar_gemini():
    # Busca a chave diretamente do Secrets do Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Configuração do modelo (Gemini 1.5 Pro é excelente para código)
    model = genai.GenerativeModel('gemini-1.5-pro')
    return model

def perguntar_gemini(prompt, system_instruction=""):
    try:
        model = configurar_gemini()
        # Instrução de sistema ajuda a focar em programação
        full_prompt = f"{system_instruction}\n\nUsuário: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erro no Gemini: {e}"
