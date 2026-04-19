import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re

def aplicar_id_afiliado(link, mkt):
    """
    Processa link do produto e adiciona ID afiliado Shopee (18316451024).
    Garante o rastro fixo e a saída do domínio do Nexus.
    """
    ID_FIXO_SHOPEE = "18316451024"
    
    if not link or len(str(link)) < 5: 
        return None
    
    # 1. LIMPEZA RADICAL: Remove lixo da IA com Regex
    raw_url = str(link).split("###")[0].split("\n")[0].strip()
    raw_url = re.sub(r'[\*\t\r]', '', raw_url) # Remove asteriscos e tabs
    raw_url = raw_url.replace(" ", "").strip()
    
    # 2. VALIDAÇÃO E PROTOCOLO
    if "shopee" not in raw_url.lower():
        if "http" not in raw_url: raw_url = "https://" + raw_url.lstrip(":/")
        return raw_url
    
    if "http" not in raw_url:
        raw_url = "https://shopee.com.br/" + raw_url.lstrip(":/")
    raw_url = raw_url.replace("http://", "https://")
    
    # 3. PROCESSAMENTO EXCLUSIVO SHOPEE
    if mkt == "Shopee":
        try:
            if "keyword=" in raw_url:
                termo = raw_url.split("keyword=")[1].split("&")[0]
                termo_codificado = urllib.parse.quote(termo)
                return f"https://shopee.com.br/search?keyword={termo_codificado}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            limpo = raw_url.split("?")[0].split("#")[0].rstrip("/")
            return f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
                
        except Exception as e:
            base = raw_url.split("?")[0].rstrip("/")
            return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
    
    return raw_url

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Garante que o nome do produto existe
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    nome_puro = sel_nome.replace("*", "").strip()
    
    # Aplica o seu ID de afiliado 18316451024
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {nome_puro}")
        st.write(f"🔗 [ABRIR NA {mkt.upper()}]({link_rastreado})")
        st.caption(f"🔐 Rastreio Shopee: `18316451024`")

  # Escolha do Estilo
    estilo = st.radio("Tom:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True, key="radio_arsenal")

    # Botão de Gerar
    if st.button(f"🔥 Gerar Munição {estilo.upper()}", use_container_width=True):
        with st.spinner("🔱 Nexus moldando munição via Groq..."):
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            try:
                # Verifica se o motor é Groq ou Gemini
                if hasattr(motor_ia_gemini, 'chat'): # Se for Groq
                    chat_completion = motor_ia_gemini.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    texto_gerado = chat_completion.choices[0].message.content
                else: # Se for Gemini
                    response = motor_ia_gemini.generate_content(prompt)
                    texto_gerado = response.text

                if texto_gerado:
                    st.session_state.res_arsenal = [texto_gerado]
                    st.rerun()
            except Exception as e:
                st.error(f"Erro na geração: {e}")
    # --- EXIBIÇÃO DAS COPIES ---
    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK: {link_rastreado}"
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Enviado ao Estúdio!")
