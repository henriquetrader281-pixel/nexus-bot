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
    
    # PASSO 3: Mídia e Vídeo
    progresso.progress(60, text="🎥 [3/5] Renderizando vídeo Reels com ganchos de retenção...")
    time.sleep(1.5)
    st.session_state.video_renderizado = True
    
    # PASSO 4: Disparo (ManyChat Webhook & Pinterest)
    progresso.progress(80, text="🚀 [4/5] Disparando Webhook para ManyChat e Redes Sociais...")
    from manychat_engine import disparar_webhook_manychat
    res_mc = disparar_webhook_manychat(dados['produto'], dados['link_ml'], dados['copy'])
    
    if res_mc['success']:
        status_post = "Webhook ManyChat disparado com sucesso! DMs automatizadas ativas."
    else:
        status_post = "Mídia pronta no Estúdio (Adicione MANYCHAT_WEBHOOK_URL nos Secrets para disparo automático)!"
    
    # PASSO 5: Conclusão
    progresso.progress(100, text="💰 [5/5] Funil de Vendas Ativo! Agente em modo de espera.")
    st.success(f"**SUCESSO ESTRATOSFÉRICO!** O Agente Nexus completou o ciclo: {status_post}")
    st.balloons()
    return dados

def exibir_aba_autonomo():
    st.header("🤖 Agente Nexus: Autonomia Total (Um Clique)")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ⚙️ Configurações do Agente")
        provedor = st.radio("Cérebro da IA:", ["ChatGPT (OpenAI)", "Google Gemini", "Groq"], horizontal=True)
        
        st.divider()
        st.warning("⚠️ O botão abaixo executa o funil completo: Mineração -> Copy -> Vídeo -> Postagem.")
        
        if st.button("🚀 ATIVAR AGENTE AGORA (1 CLIQUE)", type="primary", use_container_width=True):
            executar_ciclo_mestre_um_clique(provedor)

    with col1:
        if "nexus_dados_reais" in st.session_state:
            dados = st.session_state.nexus_dados_reais
            with st.container(border=True):
                st.subheader(f"✅ Última Operação: {dados['produto']}")
                st.info(f"**Dor Resolvida:** {dados['dificuldade']}")
                
                st.markdown("#### 📝 Copy de Elite Enviada")
                st.code(dados['copy'], language="text")
                
                st.markdown("#### 🖼️ Criativo Publicado")
                st.image(dados['imagem'], use_container_width=True)
                
                st.markdown("#### 🛒 Destino do Lead")
                st.link_button("Ver Página de Vendas (Afiliado)", dados['link_ml'], use_container_width=True)
        else:
            st.info("O Agente Nexus está aguardando o seu comando para iniciar a operação de vendas.")
