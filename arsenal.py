import streamlit as st
import nexus_copy as nxcopy  # 🔱 Mudamos aqui para evitar conflito com a biblioteca padrão do Python

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com seu ID Shopee 18316451024"""
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Limpa lixo de URL e injeta o smtt
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        bruto = st.session_state.sel_nome
        
        # 🛡️ Limpeza: Pega apenas o nome real para a IA focar na venda
        nome_limpo = bruto.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {nome_limpo}")
            st.markdown("#### 🔗 Link Rastreando Comissão")
            st.code(link_final, language="text")

        st.divider()

        # Botão padrão 2026
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", width='stretch'):
            with st.spinner("Conectando ao Cérebro de Marketing Gemini Plus..."):
                
                # 🧠 Chamando a função do arquivo nexus_copy.py
                prompt_mestre = nxcopy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                
                try:
                    # Dispara para o motor (já blindado contra erro 404 no mineracao.py)
                    resultado_bruto = miny.minerar_produtos(prompt_mestre, mkt, "gemini-1.5-pro")
                    
                    # 🧼 Limpa saudações da IA usando o nexus_copy
                    resultado = nxcopy.limpar_copy(resultado_bruto)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro no disparo do Arsenal: {e}")

        # Exibição dos Cards de Munição
        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.write(texto_copy)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.toast(f"Munição V{i+1} enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
