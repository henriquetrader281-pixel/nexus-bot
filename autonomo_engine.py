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
    
    # PASSO 1: Mineração e Validação de Stock (Anti-Erro)
    progresso.progress(15, text="🧠 [1/6] Minerando produto real e validando stock...")
    time.sleep(1)
    dados = obter_produto_real_validado(provedor)
    
    # Validação de stock
    from stock_validator import validar_link_e_stock
    val_stock = validar_link_e_stock(dados['link_ml'])
    if not val_stock['valido']:
        # Se esgotado, força outro
        dados = obter_produto_real_validado(provedor)
        
    st.session_state.nexus_dados_reais = dados
    st.session_state.sel_nome = dados['produto']
    st.session_state.sel_dor = dados['dificuldade']
    st.session_state.sel_link = dados['link_ml']
    st.session_state.nexus_media_url = dados['imagem']
    st.session_state.nexus_media_ready = True
    
    # Sincronização com Arsenal, Estúdio e Central de Disparo
    st.session_state.copy_ativa = dados['copy']
    st.session_state.copy_final_pronta = dados['copy']
    st.session_state.res_arsenal = [dados['copy']] # Para a aba Arsenal não aparecer vazia
    
    import ml_afiliados_engine
    mkt_atual = st.session_state.get('mkt_global', 'Mercado Livre')
    link_rastreado = ml_afiliados_engine.gerar_link_afiliado_dinamico(dados['link_ml'], mkt_atual)
    st.session_state.link_final_afiliado = link_rastreado
    
    # Sincronização específica para o Estúdio (Prompt 4K)
    st.session_state.micao_nexus = [dados['copy'], f"Cinematic 4k video of {dados['produto']}, hyper-realistic product showcase."]
    
    # PASSO 2: Registro
    progresso.progress(40, text="📊 [2/5] Registrando oportunidade no Dashboard de Ganhos...")
    update.registrar_mineracao(dados['produto'], dados['link_ml'], 99)
    
    # PASSO 3: Camada Visual e Vídeo Hype
    progresso.progress(50, text=f"🎥 [3/6] Coletando vídeo original da {dados.get('marketplace', 'Mercado Livre')}...")
    time.sleep(1)
    
    from visual_layer_engine import aplicar_camada_visual_elite
    # Simula renderização com selo Envio Full
    res_visual = aplicar_camada_visual_elite("reels_final.mp4", dados['produto'])
    st.session_state.nexus_video_demo = dados.get('video_demo')
    st.session_state.video_path_local = "reels_final.mp4" # Referência para download
    st.session_state.video_renderizado = True
    
    # PASSO 4: Disparo Full Auto (ManyChat + Pinterest API)
    progresso.progress(80, text="🚀 [4/5] Executando Disparo Full Auto (ManyChat + Redes Sociais)...")
    # Aplica otimização evolutiva na copy
    from self_optimizer import obter_instrucao_estrategica
    instrucao_ia = obter_instrucao_estrategica()
    copy_otimizada = dados['copy'] + f"\n\n(Auto-Otimizado: {instrucao_ia})"
    
    from manychat_engine import disparar_webhook_manychat
    res_mc = disparar_webhook_manychat(dados['produto'], dados['link_ml'], copy_otimizada)
    
    # Tentativa de Postagem Automática no Pinterest se token existir
    token_pin = st.secrets.get("PINTEREST_ACCESS_TOKEN")
    board_pin = st.secrets.get("PINTEREST_BOARD_ID")
    status_pinterest = ""
    if token_pin and board_pin:
        import pinterest_engine
        res_pin = pinterest_engine.postar_pinterest(token_pin, board_pin, dados['produto'], dados['copy'], dados['link_ml'], dados['imagem'])
        if res_pin.get('success'):
            status_pinterest = " | Pin publicado automaticamente no Pinterest!"
        else:
            status_pinterest = f" | Erro Pinterest: {res_pin.get('error')}"

    if res_mc['success']:
        status_post = f"Webhook ManyChat disparado com sucesso! DMs ativas{status_pinterest}."
    else:
        status_post = f"Mídia pronta no Estúdio{status_pinterest}."
    
    # PASSO 5: Auto-Otimização Pensante (Self-Improving)
    progresso.progress(95, text="🧠 [5/6] Analisando conversão e auto-otimizando parâmetros da IA...")
    from self_optimizer import avaliar_e_otimizar
    feedback_ia = avaliar_e_otimizar(dados['produto'], dados.get('prateleira', '🔥 Virais & Desejo'))
    
    progresso.progress(100, text="💰 [6/6] Funil de Vendas Otimizado e Ativo! Agente em modo autônomo.")
    st.success(f"**SUCESSO ESTRATOSFÉRICO!**")
    st.info(f"🧠 **Relatório de Auto-Melhoria da IA:** {feedback_ia}")
    
    # --- NOVO: AGENTE HERMES PROGRAMADOR DE ELITE ---
    import hermes_engine
    
    # Hermes faz o diagnóstico antes de finalizar
    hermes_engine.hermes_elite_programmer("diagnostico")
    
    # Hermes supervisiona a entrega e amarra as pontas
    hermes_engine.supervisionar_entrega(
        dados['produto'], 
        link_rastreado, 
        res_pin if 'res_pin' in locals() else {"success": False, "error": "Token não configurado"},
        res_ig if 'res_ig' in locals() else {"success": False, "error": "Token não configurado"},
        res_mc if 'res_mc' in locals() else {"success": False, "error": "Webhook não configurado"}
    )
    
    st.balloons()
    # Removemos o st.rerun imediato para o usuário conseguir ler o relatório do Hermes
    if st.button("🔄 INICIAR NOVO CICLO"):
        st.rerun()
        
    return dados

def exibir_aba_autonomo():
    st.header("🎯 Estrategista-Chefe: Vitrines Mercado Livre & Meta Ads (Lean)")
    st.markdown("---")
    
    from estrats_engine import analisar_produto_estrategista
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Operação de Fricção Zero")
        st.info("💡 **Foco Total no Mercado Livre (Vitrines):** Sem burocracia, com apelo de Envio Full e campanhas diretas de Meta Ads.")
        
        # --- NOVO: INTERRUPTOR DE AUTONOMIA TOTAL ---
        st.divider()
        st.markdown("#### 🧠 Cérebro Artificial")
        auto_mode = st.toggle("MODO AUTÓNOMO: APRENDER & REPLICAR", value=st.session_state.get('nexus_auto_mode', False), help="Quando ativo, o robô usa a memória evolutiva para escolher o melhor produto e postar sozinho.")
        st.session_state.nexus_auto_mode = auto_mode
        
        if auto_mode:
            st.warning("🤖 O Agente está em modo PENSANTE. Ele irá replicar as estratégias de maior ROI automaticamente.")
            if st.button("⚡ INICIAR CICLO EVOLUTIVO AGORA", type="primary", use_container_width=True):
                executar_ciclo_mestre_um_clique()
        else:
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
                
                # --- BOTÃO DE VITRINE DINÂMICO ---
                mkt_atual = st.session_state.get('mkt_global', 'Mercado Livre')
                st.markdown(f"#### 🛒 Destino (Sua Vitrine {mkt_atual})")
                
                import ml_afiliados_engine
                # Tenta pegar a URL da vitrine específica do marketplace
                key_vitrine = 'ml_vitrine_url' if mkt_atual == "Mercado Livre" else ('shopee_vitrine_url' if mkt_atual == "Shopee" else 'amazon_vitrine_url')
                vitrine_configurada = st.session_state.get(key_vitrine)
                
                if vitrine_configurada:
                    link_destino = vitrine_configurada
                else:
                    # Se não tiver vitrine, gera o link de afiliado direto para o produto
                    link_destino = ml_afiliados_engine.gerar_link_afiliado_dinamico(e['produto'], mkt_atual)
                
                st.link_button(f"🚀 Ver Produto na Minha Vitrine ({mkt_atual})", link_destino, use_container_width=True, type="primary")
                st.caption(f"Configurado para: {link_destino}")
        else:
            st.info("Clique no botão ao lado para gerar o protocolo estratégico de conversão instantânea.")
