import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024 com proteção anti-quebra"""
    # Validação rigorosa: se o link for nulo ou inválido, retorna o que recebeu
    if not link or len(str(link)) < 5 or "http" not in str(link): 
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # LIMPEZA DE ELITE: Remove asteriscos, espaços ou quebras de linha que a IA costuma colocar
    link_limpo = str(link).replace("*", "").replace(" ", "").replace("\n", "").strip()
    
    if mkt == "Shopee":
        try:
            # Pega apenas a base do link antes de qualquer interrogação antiga para não duplicar parâmetros
            base_link = link_limpo.split("?")[0]
            return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
        except:
            return link_limpo
            
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Trava de segurança: Verifica se o produto selecionado realmente existe no 'cérebro' do app
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

    # Seletor de tom de voz para a IA
    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    # Botão de Geração de Copy
    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            # Chama o gerador de prompt do módulo nexus_copy
            prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
            resultado = None  

            try:
                # Usa o motor Gemini passado pelo app.py
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
                    # Monta a mensagem final que será postada ou usada no vídeo
                    texto_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                    st.session_state.copy_ativa = texto_final
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Munição enviada ao Estúdio com Sucesso!")
