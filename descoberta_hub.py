from __future__ import annotations

import streamlit as st

import campaign_state
import radar_engine
import trends
import mineracao


def _render_scanner() -> None:
    st.subheader("🔍 Scanner de Oportunidades")
    nicho_scan = st.text_input("Nicho para varredura", value=st.session_state.get("nicho_scan", "Casa e organização"), key="nicho_scan_input")
    mkt_scan = st.selectbox("Marketplace da oportunidade", ["Mercado Livre", "Shopee", "Amazon"], key="mkt_scan_select")
    if st.button("🚀 INICIAR VARREDURA PROFUNDA", use_container_width=True, key="btn_start_scan_hub"):
        with st.spinner(f"Escaneando {mkt_scan} para {nicho_scan}..."):
            prompt = f"Liste 5 produtos promissores de {nicho_scan} no {mkt_scan}. Para cada produto, informe nome, dor, URL oficial pública quando disponível e imagem pública. Não invente links de afiliado."
            st.session_state.scan_results = mineracao.minerar_produtos(prompt, mkt_scan, None)
            st.session_state.nicho_scan = nicho_scan
            st.success("Varredura concluída. Escolha uma oportunidade para a campanha.")

    results = st.session_state.get("scan_results", "")
    if not results:
        st.info("O Scanner ainda não executou uma varredura.")
        return
    for index, line in enumerate(results.splitlines()):
        if "|" not in line:
            continue
        product_name = line.split("|", 1)[0].replace("NOME:", "").strip()
        if not product_name:
            continue
        with st.container(border=True):
            st.write(line)
            if st.button(f"🎯 USAR {product_name.upper()}", key=f"hub_scan_{index}"):
                campaign_state.set_campaign(
                    product_name=product_name,
                    pain=f"Necessidade detetada no nicho {nicho_scan}",
                    marketplace=mkt_scan,
                    source="scanner",
                )
                st.success(f"{product_name} é agora a campanha ativa.")
                st.rerun()


def exibir_descoberta() -> None:
    st.header("🔎 Descoberta de Oportunidades")
    st.caption("Scanner, Google Trends e Radar partilham o mesmo produto ativo; tendências não criam links de afiliado fictícios.")
    with st.expander("🔍 Scanner de marketplaces", expanded=True):
        _render_scanner()
    with st.expander("📈 Google Trends Brasil", expanded=False):
        trends.exibir_trends()
    with st.expander("🌍 Radar Brasil e internacional", expanded=False):
        radar_engine.exibir_radar()
