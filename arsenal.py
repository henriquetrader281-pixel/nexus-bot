import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse

def aplicar_id_afiliado(link, mkt):
    """
    BUSCA DE SOLUÇÃO NO HISTÓRICO: 
    Implementada a limpeza radical de '###' e codificação de busca.
    Garante o rastreio com ID Shopee 18316451024.
    """
    if not link or len(str(link)) < 5 or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # Limpeza de caracteres que a IA costuma "vazar" no link (buscado no histórico da conversa)
    link_limpo = str(link).split("###")[0].replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    if mkt == "Shopee":
        try:
            # SOLUÇÃO RESGATADA: Se for link de busca, reconstrói para fixar o ID corretamente
            if "search" in link_limpo and "keyword=" in link_limpo:
                base_link = link_limpo.split("keyword=")[0] + "keyword="
                termo = link_limpo.split("keyword=")[1]
                # Codifica o termo para evitar erro 404 e anexa o ID de afiliado
                return f"https://shopee.com.br/search?keyword={urllib.parse.quote(termo)}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            # Se for link direto de produto, apenas anexa o smtt
            base_link = link_limpo.split("?")[0]
            return f"{base_link}?smtt=0.0.{ID_FIXO_SHOPEE}"
        except:
            return link_limpo
            
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Trava de segurança: Recuperação de estado do cérebro (Session State)
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    
    # Processa o link injetando seu ID de Afiliado usando a lógica de busca do histórico
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        st.caption(f"🔗 Link de Comissão Pronto: {link_rastreado}")
        
        # BUSCA DE SOLUÇÃO: Sincronia com a aba Trends (Músicas Virais)
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral Detectado:** {musica}")

    # Seletor de tom de voz para a IA
    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    # Botão de Geração de Copy
    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            # O prompt agora é enriquecido com os dados do histórico (Nome + Estilo + Música)
            prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
            if musica:
                prompt += f" IMPORTANTE: Adapte o ritmo para o áudio viral: {musica}."
                
            resultado = None  

            try:
                # SOLUÇÃO RESGATADA: Uso do motor Flash (estável e grátis) configurado no app.py
                response = motor_ia_gemini.generate_content(prompt)
                if response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                else:
                    st.error("IA retornou resposta vazia.")
            except Exception as e:
                st.error(f"Erro na conexão com o Gemini: {e}")

            # Processamento do fatiamento por ### (Padronizado conforme mineracao.py)
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
                    # Monta a mensagem final com o link já rastreado e codificado
                    texto_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                    st.session_state.copy_ativa = texto_final
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Munição enviada ao Estúdio com Sucesso!")
