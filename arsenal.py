import streamlit as st
import copy  # Importante: Importa o arquivo copy.py que criamos

def aplicar_id_afiliado(link, mkt):
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    if mkt == "Shopee":
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        bruto = st.session_state.sel_nome
        
        # 🛡️ Limpeza de Elite: Remove o lixo técnico antes de enviar para a IA
        nome_limpo = bruto.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {nome_limpo}")
            st.markdown("#### 🔗 Link Rastreando Comissão")
            st.code(link_final, language="text")

        st.divider()

        # Botão atualizado para o padrão 2026 (width='stretch')
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", width='stretch'):
            with st.spinner("Conectando ao Cérebro de Marketing Gemini Plus..."):
                
                # 🧠 Aqui está a mágica: buscamos o prompt mestre no copy.py
                prompt_mestre = copy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                
                try:
                    # Dispara para o motor (já blindado contra erro 404 no mineracao.py)
                    resultado_bruto = miny.minerar_produtos(prompt_mestre, mkt, "gemini-1.5-pro")
                    
                    # 🧼 Limpa saudações da IA (Oi, aqui está...)
                    resultado = copy.limpar_copy(resultado_bruto)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    st.error(f"Erro no disparo do Arsenal: {e}")

        # Exibição das Munições
        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.write(texto_copy)
                    
                    # Botão atualizado para width='stretch'
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", width='stretch'):
                        st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.toast(f"Munição V{i+1} enviada ao Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
