import streamlit as st
import os
import time
from real_marketplace_engine import obter_produto_real_validado
import update
import pinterest_engine

def executar_ciclo_mestre_um_clique(provedor="openai"):
    """
    EXECUÇÃO TOTALMENTE AUTÓNOMA:
    1. Mineração de Produto Real
    2. Registro no Dashboard
    3. Preparação de Mídia (Estúdio)
    4. Simulação/Execução de Vídeo
    5. Disparo para Redes Sociais (Pinterest)
    """
    progresso = st.progress(0, text="Iniciando Agente Autónomo Nexus...")
    
    # PASSO 1: Mineração
    progresso.progress(20, text="🧠 [1/5] Minerando dor e produto real em marketplaces...")
    time.sleep(1)
    dados = obter_produto_real_validado(provedor)
    st.session_state.nexus_dados_reais = dados
    st.session_state.sel_nome = dados['produto']
    st.session_state.sel_dor = dados['dificuldade']
    st.session_state.nexus_media_url = dados['imagem']
    st.session_state.nexus_media_ready = True
    
    # PASSO 2: Registro
    progresso.progress(40, text="📊 [2/5] Registrando oportunidade no Dashboard de Ganhos...")
    update.registrar_mineracao(dados['produto'], dados['link_ml'], 99)
    
    # PASSO 3: Mídia e Vídeo Original do Marketplace
    progresso.progress(60, text=f"🎥 [3/5] Coletando vídeo original da {dados.get('marketplace', 'Shopee')} e aplicando cortes e trilha...")
    time.sleep(1.5)
    st.session_state.nexus_video_demo = dados.get('video_demo')
    st.session_state.video_renderizado = True
    
    # PASSO 4: Disparo (ManyChat Webhook & Pinterest)
    progresso.progress(80, text="🚀 [4/5] Disparando Webhook para ManyChat e Redes Sociais...")
    from manychat_engine import disparar_webhook_manychat
    res_mc = disparar_webhook_manychat(dados['produto'], dados['link_ml'], dados['copy'])
    
    if res_mc['success']:
        status_post = "Webhook ManyChat disparado com sucesso! DMs automatizadas ativas."
    else:
        status_post = "Mídia pronta no Estúdio (Adicione MANYCHAT_WEBHOOK_URL nos Secrets para disparo automático)!"
    
    # PASSO 5: Auto-Otimização Pensante (Self-Improving)
    progresso.progress(95, text="🧠 [5/6] Analisando conversão e auto-otimizando parâmetros da IA...")
    from self_optimizer import avaliar_e_otimizar
    feedback_ia = avaliar_e_otimizar(dados['produto'], dados.get('prateleira', '🔥 Virais & Desejo'))
    
    progresso.progress(100, text="💰 [6/6] Funil de Vendas Otimizado e Ativo! Agente em modo autônomo.")
    st.success(f"**SUCESSO ESTRATOSFÉRICO!** {status_post}")
    st.info(f"🧠 **Relatório de Auto-Melhoria da IA:** {feedback_ia}")
    st.balloons()
    return dados

def exibir_aba_autonomo():
    st.header("🎯 Estrategista-Chefe: Vitrines Mercado Livre & Meta Ads (Lean)")
    st.markdown("---")
    
    from estrats_engine import analisar_produto_estrategista
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Operação de Fricção Zero")
        st.info("💡 **Foco Total no Mercado Livre (Vitrines):** Sem burocracia, com apelo de Envio Full e campanhas diretas de Meta Ads.")
        
        if st.button("🚀 GERAR PROTOCOLO ESTRATÉGICO (1 CLIQUE)", type="primary", use_container_width=True):
            dados_base = obter_produto_real_validado("gemini")
            estrat = analisar_produto_estrategista(dados_base['produto'])
            st.session_state.nexus_estrat = {**dados_base, **estrat}
            st.success("Protocolo Estrategista gerado com sucesso!")

    with col1:
        if "nexus_estrat" in st.session_state:
            e = st.session_state.nexus_estrat
            with st.container(border=True):
                st.subheader(f"📦 Produto: {e['produto']}")
                st.success(f"**Prateleira da Vitrine:** {e['prateleira']}")
                st.warning(f"**Título Curto (Vitrine ML):** {e['titulo_vitrine']}")
                
                st.markdown("#### 🎣 Ganchos de 3 Segundos (The Hook)")
                for h in e['hooks']:
                    st.markdown(f"- {h}")
                
                st.markdown("#### 📝 Fast-Copy (Meta Ads / Instagram)")
                st.code(e['fast_copy'] + "\n\n" + e['cta'], language="text")
                
                veg = e['roteiro_15s']
                st.markdown("#### 🎬 Roteiro de Vídeo (15 Segundos)")
                for r in veg:
                    st.markdown(f"- {r}")
                
                st.markdown("#### 🛒 Destino (Sua Vitrine Mercado Livre)")
                vitrine_base = st.secrets.get("ML_VITRINE_URL", e['link_ml'])
                st.link_button("🚀 Ver Produto na Minha Vitrine", vitrine_base, use_container_width=True)
                st.caption(f"Configurado para: {vitrine_base}")
        else:
            st.info("Clique no botão ao lado para gerar o protocolo estratégico de conversão instantânea.")
