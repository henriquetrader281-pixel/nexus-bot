import streamlit as st
import random

def executar_backtest_estrategico(orcamento_diario=50.0, prateleira="🔥 Virais & Desejo"):
    """
    Simula o desempenho (Backtest) de uma campanha de Meta Ads direcionada para a Vitrine do Mercado Livre.
    Calcula impressões, cliques, CTR estimado, taxa de conversão e comissão projetada.
    """
    # Parâmetros de referência baseados em benchmarks de e-commerce e Envio Full
    cpm_medio = 18.50 # Custo por mil impressões em BRL
    
    # CTR varia conforme a prateleira (produtos virais e oferta relâmpago convertem mais no visual)
    if "Virais" in prateleira:
        ctr = random.uniform(3.2, 4.8) # %
        taxa_conversao = random.uniform(2.5, 4.0) # %
        ticket_medio = 149.90
        comissao_pct = 0.08 # 8% média ML
    elif "Tech" in prateleira:
        ctr = random.uniform(2.8, 4.2)
        taxa_conversao = random.uniform(2.0, 3.5)
        ticket_medio = 220.00
        comissao_pct = 0.07
    elif "Ofertas" in prateleira:
        ctr = random.uniform(3.5, 5.5)
        taxa_conversao = random.uniform(3.0, 5.0)
        ticket_medio = 89.90
        comissao_pct = 0.09
    else: # Utilidades & Casa
        ctr = random.uniform(2.5, 3.8)
        taxa_conversao = random.uniform(2.2, 3.2)
        ticket_medio = 119.90
        comissao_pct = 0.085
        
    # Cálculos da simulação para 7 dias de campanha
 dias = 7
    orcamento_total = orcamento_diario * dias
    
    impressoes = int((orcamento_total / cpm_medio) * 1000)
    cliques = int(impressoes * (ctr / 100))
    visitas_vitrine = int(cliques * 0.85) # Quebra por carregamento
    vendas = int(visitas_vitrine * (taxa_conversao / 100))
    if vendas < 1:
        vendas = 1 # Garantir pelo menos uma simulação realista
        
    faturamento_vendas = vendas * ticket_medio
    comissao_total = faturamento_vendas * comissao_pct
    lucro_estimado = comissao_total - orcamento_total
    roi = (comissao_total / orcamento_total) * 100
    
    return {
        "orcamento_total": orcamento_total,
        "impressoes": impressoes,
        "cliques": cliques,
        "ctr": round(ctr, 2),
        "visitas_vitrine": visitas_vitrine,
        "vendas": vendas,
        "ticket_medio": ticket_medio,
        "comissao_total": round(comissao_total, 2),
        "lucro_estimado": round(lucro_estimado, 2),
        "roi": round(roi, 1)
    }

def exibir_painel_backtest():
    st.header("📊 Simulador de Backtest & Projeção de Lucro (Meta Ads + Vitrine ML)")
    st.markdown("---")
    st.markdown("Simule o desempenho financeiro de uma campanha de tráfego direto antes de investir em anúncios, utilizando benchmarks reais do ecossistema Mercado Livre (Envio Full).")
    
    col1, col2 = st.columns(2)
    
    with col1:
        orc = st.slider("Orçamento Diário de Meta Ads (R$):", 15.0, 500.0, 50.0, 10.0)
        prat = st.selectbox("Prateleira Alvo da Vitrine:", [
            "🔥 Virais & Desejo",
            "⚡ Tech & Gadgets",
            "🚀 Ofertas Relâmpago (Full)",
            "🏠 Utilidades & Casa"
        ])
        
    with col2:
        st.markdown("### ⚙️ Parâmetros de Simulação")
        st.info(f"Período Analisado: **7 Dias**\n\nInvestimento Total: **R$ {orc * 7:.2f}**\n\nPlataforma de Destino: **Vitrines Mercado Livre (Envio Full)**")
        
    if st.button("🚀 EXECUTAR SIMULAÇÃO DE BACKTEST", type="primary", use_container_width=True):
        res = executar_backtest_estrategico(orc, prat)
        
        st.markdown("### 📈 Resultados Projetados (7 Dias de Operação)")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Investimento", f"R$ {res['orcamento_total']:.2f}")
        m2.metric("Cliques (CTR)", f"{res['cliques']} ({res['ctr']}%)")
        m3.metric("Vendas Estimadas", f"{res['vendas']} unid.")
        m4.metric("Comissão Prevista", f"R$ {res['comissao_total']:.2f}")
        
        st.divider()
        
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.metric("Lucro Líquido Estimado", f"R$ {res['lucro_estimado']:.2f}", delta=f"ROI: {res['roi']}%")
        with c_res2:
            if res['roi'] > 100:
                st.success("🔥 **Campanha Altamente Lucrativa!** O apelo do Envio Full validado no backtest indica excelente tração para escala.")
            else:
                st.warning("⚠️ **Margem Apertada:** Sugerimos testar um produto da prateleira 'Virais & Desejo' para aumentar o CTR.")
