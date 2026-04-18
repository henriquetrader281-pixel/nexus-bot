import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024 e link absoluto."""
    if not link or len(str(link)) < 5: 
        return "#"
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # 1. Limpeza Radical Blindada
    raw_url = str(link).split("###")[0].replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    # Garante que o link comece corretamente com http para sair do domínio local
    if "http" in raw_url:
        url_base = "http" + raw_url.split("http")[-1]
    else:
        url_base = "https://" + raw_url.lstrip(":/")

    if mkt == "Shopee":
        try:
            if "search" in url_base and "keyword=" in url_base:
                termo = url_base.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={urllib.parse.quote(termo)}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            # Limpa parâmetros e injeta o ID de afiliado
            base_limpa = url_base.split("?")[0].rstrip("/")
            return f"{base_limpa}?smtt=0.0.{ID_FIXO_SHOPEE}"
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
    
    # Gera o link rastreado e absoluto
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    # --- CONTAINER ÚNICO DE EXIBIÇÃO ---
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        
        # Link HTML para forçar abertura em nova aba (target="_blank")
        st.write(f'🔗 **Munição Pronta:** <a href="{link_rastreado}" target="_blank" style="color: #FF4B4B; text-decoration: none; font-weight: bold;">ABRIR PRODUTO NA {mkt.upper()} 🚀</a>', unsafe_allow_html=True)
        
        st.caption(f"Checkout Seguro: {link_rastreado}")
        
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral:** {musica}")

    # Interface de Tom de Voz
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

    # Exibição das Munições
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
