import streamlit as st
import nexus_copy as nxcopy
import update
import os

def exibir_estudio(miny, motor_ia):
    # --- HEADER PREMIUM AGÊNCIA ---
    st.markdown("""
        <div style="background: linear-gradient(135deg, #000428 0%, #004e92 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #00d2ff; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">🎥 NEXUS STUDIO PRO</h2>
            <p style="color: #00d2ff; font-size: 0.9em;">Workflow: Extensão → FetchV → Nexus → Download</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. SINCRONIZAÇÃO (Puxa do Arsenal/Extensão)
    copy_vinda = st.session_state.get("copy_ativa", "")
    produto = st.session_state.get('sel_nome', 'Produto')
    link_final = st.session_state.get('link_final_afiliado', '18316451024')

    # --- ÁREA DE CARREGAMENTO (UPLOAD) ---
    with st.container(border=True):
        st.markdown("### 📥 1. Upload do Vídeo (Capturado via FetchV)")
        video_arq = st.file_uploader("Arraste aqui o vídeo que você baixou da Shopee:", type=["mp4", "mov"])
        
        if video_arq:
            # Salva temporariamente para processar
            with open("temp_video.mp4", "wb") as f:
                f.write(video_arq.getbuffer())
            st.session_state.video_path = "temp_video.mp4"
            st.success("✅ Vídeo pronto para processamento!")

    # --- INTERFACE DE EDIÇÃO (LADO A LADO) ---
    col_preview, col_micao = st.columns([1.2, 1])

    with col_preview:
        st.markdown("#### 📺 Preview do Reels")
        if "video_path" in st.session_state:
            st.video(st.session_state.video_path)
            
            # --- ÁREA DE DOWNLOAD (SAÍDA FINAL) ---
            st.markdown("---")
            st.markdown("### 📤 2. Finalizar e Baixar")
            if st.button("⚡ RENDERIZAR VÍDEO ELITE", type="primary", use_container_width=True):
                st.balloons()
                st.success("🔥 Vídeo finalizado com sucesso!")
                
                with open(st.session_state.video_path, "rb") as file:
                    st.download_button(
                        label="📥 CLIQUE PARA BAIXAR VÍDEO FINAL",
                        data=file,
                        file_name=f"nexus_{produto.replace(' ', '_')}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                update.registrar_mineracao(produto, link_final, 100)
        else:
            st.info("Aguardando upload do vídeo para liberar o download...")

    with col_micao:
        st.markdown("#### 💎 Scripts & Prompts")
        
        # Bloco da Copy
        with st.container(border=True):
            st.markdown("📝 **COPY AIDA LIMPA**")
            legenda_pronta = nxcopy.limpar_copy(copy_vinda) if copy_vinda else "Aguardando munição..."
            st.text_area("Legenda para postar:", value=legenda_pronta, height=150)
        
        # Bloco do Prompt
        with st.container(border=True):
            st.markdown("🎨 **PROMPT MATADOR (LABS)**")
            prompt_agency = f"Cinematic product showcase of {produto}, 4k, studio lighting, hyper-realistic, bokeh effect, professional commercial style."
            st.code(prompt_agency, language="text")
            st.caption("Copie para gerar cenas extras no Google Labs")

    # Botão de navegação rápida
    if st.button("🌍 Abrir Google Labs para Criar Cenas Extras", use_container_width=True):
        st.markdown(f'<a href="https://labs.google/fx/pt/tools/flow/project/b7c52242-fa5a-4370-9975-61cc86da1483" target="_blank">Clique aqui para abrir</a>', unsafe_allow_html=True)
