import os
import time
from pathlib import Path
import streamlit as st
from real_marketplace_engine import obter_produto_real_validado
import update
import campaign_state

def executar_ciclo_mestre_um_clique(provedor="openai", publicar=False):
    # `publicar` permanece no contrato para compatibilidade com chamadas antigas;
    # a política atual é sempre preparar e guardar, nunca publicar neste ciclo.
    """
    ESTEIRA AUTÓNOMA DE PREPARAÇÃO:
    1. Mineração e validação do produto
    2. Copy AIDA, hooks, palavras-chave, legenda e áudio
    3. Imagem A e Vídeo B verticais
    4. Pacote guardado na fila persistente
    5. Links e publicação ficam manuais na Central de Disparo
    """
    progresso = st.progress(0, text="Iniciando Agente Autónomo Nexus...")
    
    # PASSO 1: Mineração e Validação de Stock (Anti-Erro)
    progresso.progress(15, text="🧠 [1/6] Minerando produto real e validando stock...")
    time.sleep(1)
    campaign = campaign_state.get_campaign()
    try:
        selected_url = campaign.get("official_affiliate_url")
        source_url = campaign.get("product_source_url") or selected_url
        if campaign.get("product_name") and (selected_url or source_url or campaign.get("image_url")):
            dados = {
                "produto": campaign["product_name"],
                "dificuldade": campaign.get("pain", "Necessidade identificada no mercado"),
                "link_ml": selected_url or source_url,
                "product_source_url": source_url,
                "official_affiliate_url": selected_url,
                "imagem": campaign.get("image_url"),
                "copy": campaign.get("copy"),
                "marketplace": campaign.get("marketplace", "Mercado Livre"),
                "nicho": campaign.get("niche"),
                "video_demo": campaign.get("video_source_url"),
                "image_verified": campaign.get("image_verified"),
                "image_source": campaign.get("image_source"),
            }
        else:
            dados = obter_produto_real_validado(provedor)

        # Validação de stock apenas quando há URL de origem real disponível.
        from stock_validator import validar_link_e_stock
        if dados.get("link_ml"):
            val_stock = validar_link_e_stock(dados["link_ml"])
            if not val_stock["valido"] and not campaign.get("product_name"):
                dados = obter_produto_real_validado(provedor)
    except Exception as mining_error:
        # Falha de descoberta não pode encerrar o Streamlit. Não criamos produto,
        # imagem ou link fictício; guardamos o diagnóstico e orientamos a próxima ação.
        reason = str(mining_error).strip() or "O Mercado Livre não devolveu dados utilizáveis."
        reason = reason[-1600:]
        campaign_state.set_campaign(mining_status="blocked", mining_error=reason, source="autonomo_blocked")
        st.session_state.nexus_mining_error = reason
        progresso.progress(15, text="⛔ Mineração bloqueada: nenhum produto seguro foi confirmado.")
        st.error("**Ciclo bloqueado com segurança.** O Mercado Livre não devolveu um anúncio com imagem pública; nenhum produto genérico foi usado.")
        st.warning("Configure `ML_ACCESS_TOKEN`/`ML_API_ACCESS_TOKEN` nos Secrets ou associe um link oficial e uma imagem pública no Modo Simples/Afiliados.")
        st.code(reason, language="text")
        st.info("Depois de corrigir a integração, execute novamente o ciclo. A publicação não foi acionada.")
        return {"status": "blocked", "reason": reason, "publication": "not_executed"}

    # O autónomo reutiliza o mesmo motor editorial do Modo Simples: palavras-chave,
    # intenção, hooks, CTA/legenda e copy AIDA antes de criar os ativos.
    from simple_mode import analisar_palavras_chave, gerar_copy
    trend_values = campaign.get("trends") or st.session_state.get("real_trends", [])
    analysis = analisar_palavras_chave(
        dados["produto"],
        dados.get("dificuldade", "Necessidade identificada no mercado"),
        ", ".join(dados.get("keywords", []) or []),
        trend_values,
    )
    campaign_state.set_from_product(dados, source=campaign.get("source") or dados.get("source") or "autonomo")
    editorial_campaign = campaign_state.get_campaign()
    copy_text, copy_warning = gerar_copy(editorial_campaign, analysis)
    campaign_state.set_campaign(
        copy=copy_text,
        copy_final=copy_text,
        hooks=analysis["hooks"],
        keywords=analysis["keywords"],
        caption=analysis["caption"],
        cta_variations=analysis["cta_variations"],
        intent=analysis["intent"],
        intent_label=analysis["intent_label"],
    )
    if copy_warning:
        st.info(copy_warning)
    dados["copy"] = copy_text
    dados["hooks"] = analysis["hooks"]
    dados["keywords"] = analysis["keywords"]
    st.session_state.nexus_dados_reais = dados
    st.session_state.res_arsenal = [copy_text]

    # A nova esteira não cria nem dispara links. Um link oficial existente é
    # apenas preservado para revisão manual posterior no Central de Disparo.
    official_url = campaign_state.get_campaign().get("official_affiliate_url") or ""
    link_rastreado = ""
    campaign_state.set_campaign(affiliate_url=official_url or None)

    # A narração também faz parte do ciclo. Em falha, a legenda permanece no vídeo,
    # mas o pacote fica marcado para revisão em vez de ser apresentado como completo.
    audio_ready = False
    try:
        import tts_engine
        voice = tts_engine.gerar_narração_ia(copy_text)
    except Exception as voice_error:
        voice = {"success": False, "error": str(voice_error)}
    if voice.get("success") and voice.get("audio_path"):
        campaign_state.set_campaign(audio_path=voice.get("audio_path"))
        audio_ready = Path(str(voice.get("audio_path"))).is_file()
    else:
        st.warning(f"Áudio não disponível; o vídeo seguirá com legenda: {voice.get('error', 'fornecedor indisponível')}.")

    # Prompt do Estúdio ligado à mesma campanha.
    campaign_state.set_campaign(prompt=f"Cinematic 4k product video of {dados['produto']}, accurate product reference, vertical 9:16.")

    # Produção real da Imagem A e do Vídeo B usando a imagem do produto.
    media_ready = False
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
        media_ready = all(Path(str(manifest.get(key))).is_file() for key in ("image_a", "video_b"))
        st.success("Imagem A e Vídeo B gerados no ciclo de 1 clique.")
    except Exception as media_error:
        st.warning(f"A campanha foi sincronizada, mas a mídia precisa de correção: {media_error}")

    # PASSO 2: Registro
    progresso.progress(40, text="📊 [2/5] Registrando oportunidade no Dashboard de Ganhos...")
    update.registrar_mineracao(dados['produto'], dados.get('link_ml') or '', 99)
    
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
    
    # PASSO 4: Montagem e armazenamento do pacote pronto para publicação manual.
    progresso.progress(80, text="📦 [4/6] Montando pacote Pinterest e guardando na fila...")
    from self_optimizer import obter_instrucao_estrategica
    instrucao_ia = obter_instrucao_estrategica()
    copy_otimizada = (dados.get("copy") or "") + f"\n\n(Auto-Otimizado: {instrucao_ia})"
    dados["copy"] = copy_otimizada
    campaign_state.set_campaign(
        copy=copy_otimizada,
        copy_final=copy_otimizada,
        preparation_status="ready_for_manual_review",
        publication_status="manual_only",
        official_affiliate_url=official_url or None,
        affiliate_url=official_url or None,
    )

    # A fila é a única saída desta etapa. Nenhuma API social, webhook ou link
    # rastreado é chamado pelo ciclo autónomo.
    from campaign_queue import save_prepared_campaign
    prepared = campaign_state.get_campaign()
    queue_status = "ready" if media_ready and audio_ready else "needs_review"
    queue_id = save_prepared_campaign(prepared, status=queue_status)
    campaign_state.set_campaign(queue_id=queue_id, queue_status=queue_status)
    dados["queue_id"] = queue_id
    dados["queue_status"] = queue_status
    dados["publication"] = "manual_only"

    res_mc = {"success": False, "skipped": True, "error": "Publicação manual: ManyChat não acionado"}
    res_pin = {"success": False, "skipped": True, "error": "Publicação manual: Pinterest não acionado"}
    res_ig = {"success": False, "skipped": True, "error": "Publicação manual: Instagram não acionado"}

    # PASSO 5: Auto-Otimização Pensante, sem modificar a política de publicação.
    progresso.progress(95, text="🧠 [5/6] Avaliando a estratégia e guardando o pacote...")
    from self_optimizer import avaliar_e_otimizar
    feedback_ia = avaliar_e_otimizar(dados['produto'], dados.get('prateleira', '🔥 Virais & Desejo'))

    progresso.progress(100, text="✅ [6/6] Pacote pronto e guardado para revisão manual.")
    if queue_status == "ready":
        st.success(f"**Pacote #{queue_id} pronto.** Produto, copy, legenda, Imagem A, Vídeo B e áudio ficaram guardados para publicação manual.")
    else:
        st.warning(f"**Pacote #{queue_id} guardado para revisão.** A copy e os criativos foram preservados, mas falta validar áudio ou mídia antes da publicação.")
    st.info(f"🧠 **Auto-Melhoria:** {feedback_ia}")
    st.warning("🔗 O link de afiliado, a revisão e a publicação ficam manuais na Central de Disparo. O ciclo autónomo não publica.")

    if st.button("🔄 INICIAR NOVO CICLO"):
        st.rerun()

    return dados

def exibir_aba_autonomo():
    st.header("⛏️ Minerador Autónomo & Estúdio de Campanhas")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Sequência única de preparação")
        st.info("💡 Uma única sequência minera, valida, cria copy, gera áudio, Imagem A e Vídeo B e guarda o pacote. Links e publicação ficam manuais.")
        
        st.divider()
        st.markdown("#### 🧠 Cérebro Artificial")
        auto_mode = st.toggle("MODO AUTÓNOMO: MINERAR & PREPARAR", value=st.session_state.get('nexus_auto_mode', False), help="A sequência é sempre a mesma; o interruptor apenas identifica que o worker pode repetir a preparação. Nenhuma publicação automática é feita.")
        st.session_state.nexus_auto_mode = auto_mode
        if auto_mode:
            st.warning("🤖 Mineração automática ativa. O pacote será guardado e a publicação continuará manual.")
        else:
            st.info("Modo manual assistido: o mesmo fluxo sequencial será executado apenas quando clicar no botão.")

        if st.button("⚡ MINERAR → COPY → ÁUDIO → IMAGEM → VÍDEO → GUARDAR", type="primary", use_container_width=True):
            # Limpa o cartão estratégico anterior para não mostrar um produto velho
            # enquanto a nova sequência está a ser processada.
            st.session_state.pop("nexus_estrat", None)
            resultado = executar_ciclo_mestre_um_clique(provedor="gemini", publicar=False)
            if isinstance(resultado, dict) and resultado.get("status") != "blocked" and resultado.get("produto"):
                st.session_state.nexus_estrat = {
                    **resultado,
                    "prateleira": resultado.get("prateleira", "Mercado Livre · Preparado"),
                    "titulo_vitrine": resultado.get("produto"),
                    "fast_copy": resultado.get("copy", ""),
                    "cta": "Ver oferta oficial",
                    "roteiro_15s": resultado.get("hooks", []),
                }

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
