import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024"""
    if not link or len(str(link)) < 10 or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    # Limpeza radical de caracteres estranhos
    link_limpo = str(link).replace("*", "").replace(" ", "").strip()
    
    if mkt == "Shopee":
        try:
            # Pega a base do link e força o seu ID de afiliado
            base_link = link_limpo.split("?")[0]
            return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
        except:
            return link_limpo
            
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # 1. Trava de segurança
    if not st.session_state.get("sel_nome") or st.session_state.sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    nome_puro = st.session_state.sel_nome.replace("*", "").strip()
    link_original = st.session_state.get("sel_link", "")
    
    # Processa o link com o seu ID fixo
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {nome_puro}")
        st.write(f"🔗 [ABRIR NA {mkt.upper()}]({link_rastreado})")
        st.caption(f"🔐 Rastreio Shopee Ativo: `{ID_FIXO_SHOPEE if mkt=='Shopee' else '---'}`")

    # 2. SELEÇÃO DO ESTILO (A variável 'estilo' é criada AQUI)
    estilo = st.radio("Tom da Munição:", ["Agressivo", "Curioso", "Prático", "Autoridade"], horizontal=True)

    # 3. GERAÇÃO DA COPY (DENTRO DA FUNÇÃO - Resolve o NameError)
    # Note que este bloco 'if' está identado para dentro do 'def exibir_arsenal'
    if st.button(f"🔥 Gerar Munição {estilo.upper()}", use_container_width=True, key=f"btn_gen_{estilo}"):
        with st.spinner("🔱 Nexus moldando roteiros de elite..."):
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            
            try:
                response = motor_ia_gemini.generate_content(prompt)
                if response and response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                    
                    # Salva no estado da sessão para exibição abaixo
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    
                    st.toast("✅ Munição Carregada!")
                    st.rerun()
            except Exception as e:
                st.error(f"🔴 Erro na IA: {e}")

    # 4. EXIBIÇÃO DAS COPIES GERADAS
    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    # Formata o texto final com o link já rastreado
                    st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK: {link_rastreado}"
                    st.toast("Enviado ao Estúdio!")
