import streamlit as st

def limpar_legenda_visual(texto):
    """Remove dados técnicos e deixa apenas o nome do produto e a copy"""
    if not texto: return ""
    # Remove as tags técnicas que o Gemini às vezes repete
    sujeiras = ["CALOR:", "VALOR:", "TICKET:", "URL:", "|"]
    linha_limpa = texto
    for sujeira in sujeiras:
        if sujeira in linha_limpa:
            linha_limpa = linha_limpa.split(sujeira)[0] # Pega só o que vem antes da primeira sujeira
    return linha_limpa.strip()

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Direção Gemini Plus")
    
    if "copy_ativa" in st.session_state:
        # Pega a copy e limpa os dados técnicos
        texto_base = limpar_legenda_visual(st.session_state.copy_ativa)
        
        # Corrige o link duplicado (Garante que não tenha https/https)
        link_cru = st.session_state.get('sel_link', '')
        if "shopee.com.br" in link_cru:
            # Pega só a base antes da interrogação e limpa
            link_limpo = link_cru.split('?')[0].replace("https://shopee.com.br/https", "https://shopee.com.br")
            link_final = f"{link_limpo}?smtt=18316451024"
        else:
            link_final = link_cru

        with st.container(border=True):
            st.markdown("#### 📝 Legenda Estratégica")
            # Exibe a legenda já limpa para o usuário
            copy_para_uso = f"{texto_base}\n\n🛒 **COMPRE AGORA:** {link_final}"
            legenda_editavel = st.text_area("Refine a munição final:", value=copy_para_uso, height=200)
            
            if st.button("📋 COPIAR TEXTO + LINK", use_container_width=True):
                st.toast("Copiado para a área de transferência!")
        
        # ... resto do código do botão ANALISAR VÍDEO ...
