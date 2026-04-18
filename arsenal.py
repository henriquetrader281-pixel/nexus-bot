import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio 18316451024 e força o link a ser absoluto."""
    if not link or len(str(link)) < 5: 
        return "#"
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # 1. Limpeza Radical: Remove lixo da IA sem quebrar o protocolo
    raw_url = str(link).split("###")[0].replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    # FORÇA O PROTOCOLO ABSOLUTO (Evita o erro https?)
    if "http" not in raw_url:
        url_base = "https://shopee.com.br/" + raw_url.lstrip(":/")
    else:
        url_base = "http" + raw_url.split("http")[-1]

    if mkt == "Shopee":
        try:
            # Lógica para links de busca (keyword)
            if "keyword=" in url_base:
                termo = url_base.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={urllib.parse.quote(termo)}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            # Lógica para links diretos de produtos
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
    
    # Gera o link final rastreado
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        
        # LINK HTML: target="_blank" obriga o navegador a abrir uma nova aba externa
        st.write(f'🔗 **Munição Pronta:** <a href="{link_rastreado}" target="_blank" style="color: #FF4B4B; text-decoration: none; font-weight: bold; border: 1px solid #FF4B4B; padding: 5px 10px; border-radius: 5px;">ABRIR PRODUTO NA {mkt.upper()} 🚀</a>', unsafe_allow_html=True)
        
        st.caption(f"Checkout Seguro: {link_rastreado}")
        
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral:** {musica}")

    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
            
            try:
                # Chama o modelo configurado no app.py
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
                st.info("💡 Verifique se o nome do modelo no app.py está como 'gemini-1.5-flash' (sem o prefixo models/)")

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
