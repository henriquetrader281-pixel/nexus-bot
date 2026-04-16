import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024 com proteção anti-quebra"""
    if not link or len(str(link)) < 10 or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    link_limpo = str(link).replace("*", "").replace(" ", "").strip()
    
    if mkt == "Shopee":
        try:
            base_link = link_limpo.split("?")[0]
            return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
        except:
            return link_limpo
            
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Trava de segurança
    if not st.session_state.get("sel_nome") or st.session_state.sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    nome_puro = st.session_state.sel_nome
    link_original = st.session_state.get("sel_link", "")
    
    # Processa o link
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {nome_puro}")
        st.caption(f"🔗 Link de Comissão Pronto: {link_rastreado}")

    # Seletor de tom
    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    # Botão de Geração
    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            resultado = None  # Garante que a variável existe antes do try

            try:
                response = motor_ia_gemini.generate_content(prompt)
                resultado = nxcopy.limpar_copy(response.text)
            except Exception as e:
                st.error(f"Erro na conexão com o Gemini Pro: {e}")

            # Só processa se gerou resultado com sucesso
            if resultado:
                if "###" in resultado:
                    st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 20]
                else:
                    st.session_state.res_arsenal = [resultado.strip()]
                st.rerun()

    # Exibição das copies geradas
    if st.session_state.get("res_arsenal"):
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    texto_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                    st.session_state.copy_ativa = texto_final
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Munição enviada ao Estúdio com Sucesso!")
