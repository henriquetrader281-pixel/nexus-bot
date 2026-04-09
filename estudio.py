import streamlit as st
import requests
import re
import os
import update
import mineracao as miny

# --- 1. O MOTOR DE BUSCA (SCRAPER) ---
def caçar_video_shopee(url_produto):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url_produto, headers=headers, timeout=10)
        # O segredo: Procuramos por links .mp4 que a Shopee esconde no JSON de metadados da página
        links = re.findall(r'https://[^\s"]+\.mp4', res.text)
        
        if links:
            # Limpa o link de barras invertidas comuns em JSON
            video_url = links[0].replace('\\u002f', '/').replace('\\/', '/')
            return video_url
        return None
    except Exception as e:
        st.error(f"Erro no rastreio: {e}")
        return None

# --- 2. INTERFACE DO ESTÚDIO ---
def exibir_estudio(miny_motor, motor_ia):
    st.markdown("### 🛰️ Central de Captura e Edição Nexus")

    # Passo 1: Caça ao Link
    with st.container(border=True):
        st.markdown("#### 🔍 Passo 1: Rastrear Vídeo Original")
        url_target = st.text_input("Cole o link do anúncio da Shopee:", placeholder="https://shopee.com.br/produto...")
        
        if st.button("🛰️ INICIAR CAÇA AO VÍDEO", width='stretch'):
            with st.spinner("Navegando nos servidores da Shopee..."):
                video_link = caçar_video_shopee(url_target)
                if video_link:
                    st.session_state.video_encontrado = video_link
                    st.success("🎯 Alvo localizado!")
                    st.code(video_link, language="text")
                else:
                    st.error("❌ Vídeo não encontrado. Tente outro link ou verifique se o anúncio tem vídeo.")

    # Passo 2: Visualização e Preparo
    if "video_encontrado" in st.session_state:
        st.video(st.session_state.video_encontrado)
        
        st.divider()
        st.markdown("#### 📝 Passo 2: Aplicar Munição do Arsenal")
        copy_ativa = st.session_state.get("copy_ativa", "Selecione uma copy no Arsenal primeiro.")
        
        legenda_final = st.text_area("Legenda Final (com Gatilho ManyChat):", value=copy_ativa, height=150)

        # Ações Finais
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📽️ GERAR ROTEIRO TÁTICO", width='stretch'):
                prompt = f"Crie um roteiro de 15 segundos baseado nesta legenda: {legenda_final}"
                roteiro = miny_motor.minerar_produtos(prompt, "Shopee", motor_ia)
                st.info(roteiro)
        
        with col2:
            if st.button("🚀 SALVAR NO RAIO-X", type="primary", width='stretch'):
                # Salva os dados no Dashboard (update.py)
                sucesso = update.aplicar_seo_viral(
                    st.session_state.get('sel_nome', 'Produto'), 
                    st.session_state.get('sel_link', url_target), 
                    "Shopee"
                )
                if sucesso:
                    st.balloons()
                    st.toast("Produto registrado no Dashboard!")

    else:
        st.info("💡 Cole um link da Shopee acima para começar a produção.")
