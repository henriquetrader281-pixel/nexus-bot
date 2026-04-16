import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Limpa a URL e injeta o ID de afiliado corretamente"""
    if not link or link == "#" or "http" not in str(link):
        return link
        
    ID_FIXO_SHOPEE = "18316451024"
    
    # Remove asteriscos e espaços que a IA possa ter inserido na URL
    link_limpo = str(link).replace("*", "").replace(" ", "").strip()
    
    if mkt == "Shopee":
        # Remove parâmetros antigos para não duplicar o '?' e causar erro 404
        base_link = link_limpo.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.get('mkt_global', 'Shopee')
        
        # Limpeza do nome para não bugar a IA
        nome_puro = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").replace("*", "").strip()
        
        # Gera o link rastreado e limpo
        link_rastreado = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Alvo Ativo:** {nome_puro}")
            st.caption(f"🔗 Link de Comissão: {link_rastreado}")

        estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

        if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
            with st.spinner("Gemini moldando roteiros de elite..."):
                prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
                
                # --- No arsenal.py, dentro do botão de gerar copy ---
try:
    # Tenta gerar o conteúdo com o motor vindo do app.py
    response = motor_ia_gemini.generate_content(prompt)
    
    if response and response.text:
        resultado = nxcopy.limpar_copy(response.text)
        # ... resto da sua lógica de split por ### ...
    else:
        st.error("A IA retornou uma resposta vazia. Tente novamente.")
except Exception as e:
    st.error(f"Erro na IA (Gemini): {e}")
    st.info("Dica: Verifique se a sua GEMINI_API_KEY está correta nos Secrets do Streamlit.")

        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
                with st.container(border=True):
                    st.write(texto_copy)
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", use_container_width=True):
                        st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_rastreado}"
                        st.session_state.link_final_afiliado = link_rastreado
                        st.toast("Munição enviada com Link corrigido!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
