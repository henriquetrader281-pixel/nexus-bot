import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse

def aplicar_id_afiliado(link, mkt):
    """
    Garante o rastreio com ID Shopee 18316451024.
    TRAVA DE ELITE: Garante que o link seja ABSOLUTO para sair do domínio do Nexus.
    """
    if not link or len(str(link)) < 5: 
        return "#"
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # 1. Limpeza Radical (Preservando o essencial)
    # Remove lixo da IA e garante que não haja espaços que quebram a URL
    url_base = str(link).split("###")[0].replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    # 2. Reconstrução do Protocolo (Evita apontar para o próprio Nexus)
    if "http" not in url_base:
        url_base = "https://" + url_base.lstrip(":/")
    else:
        # Garante que não ficou nada grudado antes do https (como : ou texto)
        url_base = "https://" + url_base.split("http")[-1].lstrip("s:/")

    if mkt == "Shopee":
        try:
            # Se for link de busca
            if "search" in url_base and "keyword=" in url_base:
                termo = url_base.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={urllib.parse.quote(termo)}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            # Se for link de produto direto
            limpo = url_base.split("?")[0].rstrip("/")
            return f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
        except:
            return url_base
            
    return url_base

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    
    # Processa o link garantindo que ele seja externo
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        
        # --- COMPONENTE DE LINK BLINDADO ---
        # Usamos o link direto para garantir que o navegador trate como URL externa
        st.markdown(f"🔗 **Link de Afiliado:** [ABRIR PRODUTO NA {mkt.upper()}]({link_rastreado})")
        st.caption(f"Checkout Seguro: {link_rastreado}")
        
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral:** {musica}")

    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
            if musica:
                prompt += f" Considere o áudio: {musica}."
                
            try:
                response = motor_ia_gemini.generate_content(prompt)
                if response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    st.rerun()
            except Exception as e:
                st.error(f"Erro no Gemini: {e}")

    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    texto_final = f"{texto_copy}\n\n🛒 LINK: {link_rastreado}"
                    st.session_state.copy_ativa = texto_final
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Munição enviada!")
