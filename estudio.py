import streamlit as st
import os

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    pass

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus | Edição na Nuvem 🔱")
    
    if "copy_ativa" in st.session_state and st.session_state.copy_ativa != "":
        st.success("✅ Copy Matadora Recebida!")
        
        link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
        link_base = link_raw.split('?')[0].split('|')[0].strip()
        link_final = f"{link_base}?smtt=18316451024"
        
        st.text_area("Legenda do Post (Copia e Cola no Instagram):", f"{st.session_state.copy_ativa}\n\n🛒 COMPRE AQUI: {link_final}", height=150)
        
        st.divider()
        st.markdown("#### ⚙️ Motor de Renderização (Streamlit Cloud)")
        
        # Lendo e salvando direto na raiz do GitHub / Nuvem
        video_base = "video_modelo_nexus.mp4" 
        caminho_final = "reel_pronto_nexus.mp4"
        
        if st.button("🎞️ INICIAR EDIÇÃO E GERAR DOWNLOAD", type="primary"):
            with st.spinner("IA fatiando a copy e renderizando vídeo na nuvem..."):
                
                prompt_edicao = f"Divida esta copy em 3 partes curtas separadas por '|': [HOOK] | [DESEJO] | [CTA]. Copy: {st.session_state.copy_ativa}"
                
                try:
                    mapa_edicao = miny.minerar_produtos(prompt_edicao, "Shopee", motor_ia)
                    partes_texto = mapa_edicao.split('|')
                    
                    texto_hook = partes_texto[0].strip() if len(partes_texto) > 0 else "Olha isso!"
                    texto_meio = partes_texto[1].strip() if len(partes_texto) > 1 else st.session_state.copy_ativa
                    texto_cta = partes_texto[2].strip() if len(partes_texto) > 2 else "Link na Bio!"
                    
                    if os.path.exists(video_base):
                        # Carrega o vídeo cru que está no GitHub
                        video = VideoFileClip(video_base).subclip(0, 15)
                        
                        txt_hook = TextClip(texto_hook, fontsize=50, color='white', stroke_color='black', stroke_width=2, method='caption', size=video.size).set_position('center').set_start(0).set_end(3)
                        txt_meio = TextClip(texto_meio, fontsize=45, color='white', stroke_color='black', stroke_width=2, method='caption', size=video.size).set_position('center').set_start(3).set_end(10)
                        txt_cta = TextClip(texto_cta, fontsize=55, color='yellow', stroke_color='black', stroke_width=3, method='caption', size=video.size).set_position('center').set_start(10).set_end(15)
                        
                        video_final = CompositeVideoClip([video, txt_hook, txt_meio, txt_cta])
                        
                        # Salva temporariamente na nuvem do Streamlit
                        video_final.write_videofile(caminho_final, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        st.success("🚀 VÍDEO RENDERIZADO COM SUCESSO!")
                        
                        # GERA O BOTÃO DE DOWNLOAD DIRETO PARA O SEU CELULAR/PC
                        with open(caminho_final, "rb") as file:
                            btn = st.download_button(
                                label="📥 BAIXAR REEL PARA A GALERIA",
                                data=file,
                                file_name="reel_viral_pronto.mp4",
                                mime="video/mp4",
                                type="primary"
                            )
                        
                        st.balloons()
                        st.session_state.copy_ativa = ""
                        
                    else:
                        st.error(f"⚠️ O arquivo '{video_base}' não foi encontrado! Faça o upload dele para a raiz do seu repositório no GitHub.")
                
                except Exception as e:
                    st.error(f"Erro no motor de renderização: {e}\n(Verifique se o pacote 'moviepy' está no seu arquivo requirements.txt do GitHub).")
    else:
        st.warning("⚠️ Volte no Arsenal, gere as copys e clique em 'Usar V1' para enviar o texto para a ilha de edição.")
