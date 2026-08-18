import os
import time
from pathlib import Path
import streamlit as st
from real_marketplace_engine import obter_produto_real_validado
import update
import pinterest_engine
import campaign_state

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
    campaign = campaign_state.get_campaign()
    selected_url = campaign.get("official_affiliate_url")
    if campaign.get("product_name") and selected_url:
        dados = {
            "produto": campaign["product_name"],
            "dificuldade": campaign.get("pain", "Necessidade identificada no mercado"),
            "link_ml": selected_url,
            "imagem": campaign.get("image_url"),
            "copy": campaign.get("copy") or f"Descubra como {campaign['product_name']} pode resolver este problema.",
            "marketplace": campaign.get("marketplace", "Mercado Livre"),
            "nicho": campaign.get("niche"),
            "video_demo": campaign.get("video_source_url"),
        }
    else:
        dados = obter_produto_real_validado(provedor)

    # Validação de stock apenas quando há URL real disponível.
    from stock_validator import validar_link_e_stock
    if dados.get("link_ml"):
        val_stock = validar_link_e_stock(dados["link_ml"])
        if not val_stock["valido"] and not campaign.get("product_name"):
            dados = obter_produto_real_validado(provedor)

    dados["copy"] = dados.get("copy") or f"Conheça {dados['produto']} e veja a oferta oficial."
    campaign_state.set_from_product(dados, source=campaign.get("source") or "autonomo")
    st.session_state.nexus_dados_reais = dados
    st.session_state.res_arsenal = [dados["copy"]]

    import ml_afiliados_engine
    mkt_atual = dados.get("marketplace") or st.session_state.get("mkt_global", "Mercado Livre")
    link_rastreado = ml_afiliados_engine.gerar_link_afiliado_dinamico(dados["link_ml"], mkt_atual)
    campaign_state.set_campaign(copy=dados["copy"], copy_final=dados["copy"], affiliate_url=link_rastreado)

    # Prompt do Estúdio ligado à mesma campanha.
    campaign_state.set_campaign(prompt=f"Cinematic 4k product video of {dados['produto']}, accurate product reference, vertical 9:16.")

    # Produção real da Imagem A e do Vídeo B usando a imagem do produto.
    try:
        from media_pipeline import generate_campaign_media
        manifest = generate_campaign_media(campaign_state.get_campaign())
        campaign_state.set_campaign(
            source_image_path=manifest.get("source_image_path"),
            image_path=manifest["image_a"],
            video_path=manifest["video_b"],
            image_url=manifest["product"].get("image_url"),
            media_manifest=manifest,
        )
        st.success("Imagem A e Vídeo B gerados no ciclo de 1 clique.")
    except Exception as media_error:
        st.warning(f"A campanha foi sincronizada, mas a mídia precisa de correção: {media_error}")

    # PASSO 2: Registro
    progresso.progress(40, text="📊 [2/5] Registrando oportunidade no Dashboard de Ganhos...")
    update.registrar_mineracao(dados['produto'], dados['link_ml'], 99)
    
    # PASSO 3: Camada Visual e Vídeo Hype
    progresso.progress(50, text=f"🎥 [3/6] Coletando vídeo original da {dados.get('marketplace', 'Mercado Livre')}...")
    time.sleep(1)

    from visual_layer_engine import aplicar_camada_visual_elite
    # Só aplica a camada visual se existir uma fonte local; o ciclo não deve cair
    # por falta de um arquivo opcional de vídeo.
    video_fonte = Path("reels_final.mp4")
    if video_fonte.exists():
        aplicar_camada_visual_elite(str(video_fonte), dados['produto'])
    campaign_state.set_campaign(video_source_url=dados.get("video_demo"))
    st.session_state.video_renderizado = False
    
    # PASSO 4: Disparo Full Auto (ManyChat + Pinterest API)
    progresso.progress(80, text="🚀 [4/5] Executando Disparo Full Auto (ManyChat + Redes Sociais)...")
    # Aplica otimização evolutiva na copy
    from self_optimizer import obter_instrucao_estrategica
    instrucao_ia = obter_instrucao_estrategica()
    copy_otimizada = dados['copy'] + f"\n\n(Auto-Otimizado: {instrucao_ia})"
    
    from manychat_engine import disparar_webhook_manychat
    res_mc = disparar_webhook_manychat(dados['produto'], dados['link_ml'], copy_otimizada)
    
    # Prepara o registo analítico antes do disparo, mantendo o URL oficial intacto.
    import metrics_store
    media_campaign = campaign_state.get_campaign()
    asset_image_url = media_campaign.get("image_url") or dados.get("imagem")
    campaign_id = metrics_store.create_campaign(
        dados.get("marketplace", "Mercado Livre"),
        dados["link_ml"],
        dados["produto"],
    )
    creative_id = metrics_store.create_creative(
        campaign_id,
        "image_a",
        dados["produto"],
        dados["copy"],
        "Ver oferta oficial",
        asset_url=asset_image_url,
        width=1000,
        height=1500,
        status="ready",
    )
    st.session_state.metrics_campaign_id = campaign_id
    st.session_state.metrics_creative_id = creative_id

    # Tentativa de postagem automática no Pinterest se os Secrets existirem.
    def _safe_secret(name):
        try:
            value = st.secrets.get(name)
        except Exception:
            value = None
        return value

    token_pin = _safe_secret("PINTEREST_ACCESS_TOKEN")
    board_pin = _safe_secret("PINTEREST_BOARD_ID")
    res_pin = {"success": False, "skipped": True, "error": "Pinterest não configurado"}
    status_pinterest = ""
    if token_pin and board_pin and asset_image_url:
        import pinterest_engine
        res_pin = pinterest_engine.postar_pinterest(token_pin, board_pin, dados['produto'], dados['copy'], dados['link_ml'], asset_image_url)
        if res_pin.get('success'):
            pin_data = res_pin.get("data") or {}
            publication_id = metrics_store.record_publication(
                creative_id,
                "pinterest",
                external_post_id=str(pin_data.get("id")) if pin_data.get("id") else None,
                external_url=res_pin.get("url"),
                status="published",
            )
            st.session_state.metrics_publication_id = publication_id
            status_pinterest = " | Pin publicado automaticamente no Pinterest e registado nas métricas!"
        else:
            status_pinterest = f" | Erro Pinterest: {res_pin.get('error')}"
            res_pin["skipped"] = False
    elif not asset_image_url:
        res_pin = {"success": False, "skipped": False, "error": "Imagem pública do produto não disponível"}
        status_pinterest = " | Imagem pública ausente para o Pinterest"

    res_ig = {"success": False, "skipped": True, "detail": "Instagram não acionado neste ciclo"}
    if res_mc['success']:
        status_post = f"Webhook ManyChat disparado com sucesso! DMs ativas{status_pinterest}."
    else:
        status_post = f"Mídia pronta no Estúdio{status_pinterest}."
    
    # PASSO 5: Auto-Otimização Pensante (Self-Improving)
    progresso.progress(95, text="🧠 [5/6] Analisando conversão e auto-otimizando parâmetros da IA...")
    from self_optimizer import avaliar_e_otimizar
    feedback_ia = avaliar_e_otimizar(dados['produto'], dados.get('prateleira', '🔥 Virais & Desejo'))
    
    progresso.progress(100, text="💰 [6/6] Funil de Vendas Otimizado e Ativo! Agente em modo autônomo.")
    st.success("**Ciclo autónomo executado.** Consulte a auditoria Hermes abaixo antes de considerar a operação aprovada.")
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
