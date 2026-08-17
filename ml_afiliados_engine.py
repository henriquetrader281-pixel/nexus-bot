import streamlit as st
import campaign_state

def gerar_link_afiliado_dinamico(url_original, marketplace, tracking_id=None):
    """
    Gera link de afiliado baseado no marketplace selecionado.
    """
    if not tracking_id:
        if marketplace == "Mercado Livre":
            tracking_id = st.session_state.get('ml_tracking_id', st.secrets.get("ML_TRACKING_ID", "18316451024"))
        elif marketplace == "Shopee":
            tracking_id = st.session_state.get('shopee_tracking_id', st.secrets.get("SHOPEE_TRACKING_ID", "18316451024"))
        else:
            tracking_id = st.session_state.get('amazon_tracking_id', st.secrets.get("AMAZON_TRACKING_ID", "nexus-20"))

    if marketplace == "Mercado Livre":
        # Links emitidos pelo Portal do Afiliado são a fonte de verdade.
        # Nunca acrescentar UTM ou reconstruir matt_word/matt_tool.
        if any(marker in str(url_original) for marker in ("meli.la/", "matt_word=", "matt_tool=")):
            return str(url_original)
        if "mercadolivre.com.br" in str(url_original) and "?" in str(url_original):
            return str(url_original)
        if "mercadolivre.com.br" in str(url_original):
            return f"{url_original}?utm_source=nexus_bot&utm_medium=afiliado&utm_campaign={tracking_id}"
        search = url_original.replace(" ", "%20")
        return f"https://lista.mercadolivre.com.br/{search}#D[A:{search},L:undefined,utm_source=nexus_bot,utm_campaign={tracking_id}]"
    
    elif marketplace == "Shopee":
        search = url_original.replace(" ", "%20")
        return f"https://shopee.com.br/search?keyword={search}&smtt=0.0.{tracking_id}"
    
    elif marketplace == "Amazon":
        search = url_original.replace(" ", "+")
        return f"https://www.amazon.com.br/s?k={search}&tag={tracking_id}"
    
    return url_original

def exibir_config_ml():
    st.markdown("### 🤝 Central de Afiliados & Vitrines")
    st.info("Cole aqui o link oficial criado no portal de afiliados. O Nexus preserva o URL recebido e usa-o para buscar a imagem real e produzir os criativos.")
    campanha = campaign_state.get_campaign()
    link_oficial = st.text_input(
        "Link oficial do produto ou da Vitrine",
        value=campanha.get("official_affiliate_url", ""),
        placeholder="https://meli.la/...",
        key="official_affiliate_input",
    )
    if st.button("🔗 VINCULAR LINK À CAMPANHA", type="primary", use_container_width=True):
        if not link_oficial.startswith(("http://", "https://")):
            st.error("Cole uma URL HTTP(S) válida criada no portal oficial.")
        else:
            campaign_state.set_campaign(
                official_affiliate_url=link_oficial.strip(),
                affiliate_url=link_oficial.strip(),
                marketplace=st.session_state.get("mkt_global", "Mercado Livre"),
                source="affiliate_portal",
            )
            st.success("Link oficial vinculado à campanha ativa. O Estúdio já pode gerar a mídia.")

    mkt_config = st.selectbox("Configurar Marketplace:", ["Mercado Livre", "Shopee", "Amazon"])
    
    with st.expander(f"⚙️ CONFIGURAR CONTA: {mkt_config.upper()}", expanded=True):
        if mkt_config == "Mercado Livre":
            st.info("Inscreva-se no [Programa de Afiliados ML](https://www.mercadolivre.com.br/afiliados).")
            key_id = 'ml_tracking_id'
            key_url = 'ml_vitrine_url'
        elif mkt_config == "Shopee":
            st.info("Inscreva-se no [Programa de Afiliados Shopee](https://affiliate.shopee.com.br/).")
            key_id = 'shopee_tracking_id'
            key_url = 'shopee_vitrine_url'
        else:
            st.info("Inscreva-se no [Programa de Associados Amazon](https://associados.amazon.com.br/).")
            key_id = 'amazon_tracking_id'
            key_url = 'amazon_vitrine_url'

        tracking_id = st.text_input(f"Seu ID de Rastreamento ({mkt_config}):", 
                                    value=st.session_state.get(key_id, ''),
                                    placeholder="Ex: seu_id_01")
        
        vitrine_url = st.text_input(f"URL da sua Vitrine {mkt_config} (Opcional):", 
                                     value=st.session_state.get(key_url, ''),
                                     placeholder=f"https://www.{mkt_config.lower().replace(' ', '')}.com.br/vitrine")
        
        if st.button(f"💾 SALVAR CONFIGURAÇÕES {mkt_config.upper()}", use_container_width=True):
            st.session_state[key_id] = tracking_id
            st.session_state[key_url] = vitrine_url
            st.success(f"✅ Configurações para {mkt_config} salvas!")
            st.balloons()

    st.divider()
    
    st.markdown("#### 📊 Status da Integração")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cliques Totais", "0", "+100%")
    c2.metric("Vendas Estimadas", "R$ 0,00", "0%")
    c3.metric("Comissão Pendente", "R$ 0,00", "0%")
    
    st.caption("Nota: Os dados acima são projeções baseadas no tráfego gerado pelo Nexus. Consulte o painel oficial do ML para valores reais.")
