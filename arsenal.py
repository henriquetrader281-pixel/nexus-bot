import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024 com proteção anti-quebra"""
    if not link or len(str(link)) < 5 or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # LIMPEZA DE ELITE: Remove asteriscos, espaços ou quebras de linha
    link_limpo = str(link).replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    if mkt == "Shopee":
        try:
            # Melhoria: Garante que caracteres especiais no link de busca sejam codificados
            base_parts = link_limpo.split("?")
            base_link = base_parts[0]
            
            # Se já for um link de busca, codifica o termo para não dar erro 404
            if "search" in base_link and "keyword=" in link_limpo:
                params = urllib.parse.parse_qs(base_parts[1])
                keyword = params.get('keyword', [''])[0]
                return f"https://shopee.com.br/search?keyword={urllib.parse.quote(keyword)}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            return f"{base_link}?smtt=0.0.{ID_FIXO_SHOPEE}"
        except:
            return link_limpo
            
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Trava de segurança: Verifica o 'cérebro' do app
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    
    # Processa o link injetando seu ID de Afiliado
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        st.caption(f"🔗 Link de Comissão Pronto: {link_rastreado}")
        
        # Melhoria Visual: Puxa o áudio selecionado na aba Trends se existir
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral Detectado:** {musica}")

    # Seletor de tom de voz para a IA
    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    # Botão de Geração de Copy
    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            # Melhoria: O prompt agora leva em conta a música se ela estiver selecionada
            prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
            if musica:
                prompt += f" Considere que o vídeo usará o áudio viral: {musica}."
                
            resultado = None  

            try:
                response = motor_ia_gemini.generate_content(prompt)
                if response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                else:
                    st.error("IA retornou resposta vazia.")
            except Exception as e:
                st.error(f"Erro na conexão com o Gemini: {e}")

            # Processamento do fatiamento por ###
            if resultado:
                if "###" in resultado:
                    st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 15]
                else:
                    st.session_state.res_arsenal = [resultado.strip()]
                st.rerun()

    # Exibição das Munições Geradas
    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                
                # Botão de Envio para a aba Estúdio/Postador
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    texto_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                    st.session_state.copy_ativa = texto_final
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Munição enviada ao Estúdio com Sucesso!")
