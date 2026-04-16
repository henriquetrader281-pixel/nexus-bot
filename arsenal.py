import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com seu ID Shopee 18316451024 e evita erro 404"""
    if not link or link == "#" or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # LIMPEZA DE SEGURANÇA: Remove asteriscos ou espaços que a IA possa ter inserido
    link_limpo = str(link).replace("*", "").replace(" ", "").strip()
    
    if mkt == "Shopee":
        # Pega apenas a base do link antes de qualquer interrogação antiga
        base_link = link_limpo.split("?")[0]
        # Monta a URL de afiliado correta
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Verifica se há produto selecionado no st.session_state
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.get('mkt_global', 'Shopee')
        
        # Limpa o nome vindo do Scanner
        nome_puro = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").replace("*", "").strip()
        
        # Link rastreado e limpo
        link_rastreado = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Alvo Ativo:** {nome_puro}")
            st.caption(f"🔗 Link de Comissão: {link_rastreado}")

        # Seletor de tom de voz
        estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

        if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
            with st.spinner("Gemini moldando roteiros de elite..."):
                prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
                
                try:
                    response = motor_ia_gemini.generate_content(prompt)
                    resultado = nxcopy.limpar_copy(response.text)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no Gemini: {e}")

        # --- AQUI ESTAVA O ERRO DE INDENTAÇÃO (LINHA 57) ---
        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Munição V{i+1}")
                    st.write(texto_copy)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                        texto_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                        st.session_state.copy_ativa = texto_final
                        st.session_state.link_final_afiliado = link_rastreado
                        st.toast("Munição enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
