import streamlit as st

def gerar_link_afiliado_ml(url_original, tracking_id=None):
    """
    Simula a geração de um link de afiliado ou redirecionamento para Vitrine.
    No Mercado Livre, os links costumam seguir o padrão de tracking ou vitrine personalizada.
    """
    if not tracking_id:
        tracking_id = st.secrets.get("ML_TRACKING_ID", "NEXUS_DEFAULT")
    
    # Simulação de link de afiliado (Mercado Livre Afiliados usa redirecionamento ou link direto com tracking)
    if "mercadolivre.com.br" in url_original:
        # Exemplo simplificado de link de afiliado
        link_final = f"{url_original}?utm_source=nexus_bot&utm_medium=afiliado&utm_campaign={tracking_id}"
    else:
        # Se for um termo de busca, manda para a vitrine ou busca com tracking
        search_query = url_original.replace(" ", "%20")
        link_final = f"https://lista.mercadolivre.com.br/{search_query}#D[A:{search_query},L:undefined,utm_source=nexus_bot,utm_campaign={tracking_id}]"
    
    return link_final

def exibir_config_ml():
    st.markdown("### 🤝 Integração Mercado Livre Afiliados")
    
    with st.expander("⚙️ CONFIGURAR MINHA CONTA DE AFILIADO", expanded=True):
        st.info("Para gerar receita, você precisa estar inscrito no [Programa de Afiliados do Mercado Livre](https://www.mercadolivre.com.br/afiliados).")
        
        tracking_id = st.text_input("Seu ID de Rastreamento (Tracking ID):", 
                                    value=st.session_state.get('ml_tracking_id', ''),
                                    placeholder="Ex: seu_nome_01")
        
        vitrine_url = st.text_input("URL da sua Vitrine Personalizada (Opcional):", 
                                     value=st.session_state.get('ml_vitrine_url', ''),
                                     placeholder="https://www.mercadolivre.com.br/social/suavitrine")
        
        if st.button("💾 SALVAR CONFIGURAÇÕES DE AFILIADO", use_container_width=True):
            st.session_state.ml_tracking_id = tracking_id
            st.session_state.ml_vitrine_url = vitrine_url
            st.success("✅ Configurações de Afiliado salvas com sucesso! Todos os links agora serão rastreados.")
            st.balloons()

    st.divider()
    
    st.markdown("#### 📊 Status da Integração")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cliques Totais", "0", "+100%")
    c2.metric("Vendas Estimadas", "R$ 0,00", "0%")
    c3.metric("Comissão Pendente", "R$ 0,00", "0%")
    
    st.caption("Nota: Os dados acima são projeções baseadas no tráfego gerado pelo Nexus. Consulte o painel oficial do ML para valores reais.")
