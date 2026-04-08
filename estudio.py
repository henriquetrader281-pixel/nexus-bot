import streamlit as st
import os
# Importação da biblioteca de edição em Python
# (Requer: pip install moviepy)
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    pass

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio Nexus | Edição Neural 🔱")
    
    if "copy_ativa" in st.session_state and st.session_state.copy_ativa != "":
        st.success("✅ Copy Matadora Recebida!")
        
        link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
        link_base = link_raw.split('?')[0].split('|')[0].strip()
        link_final = f"{link_base}?smtt=18316451024"
        
        st.text_area("Legenda do Post (Copia e Cola no Instagram):", f"{st.session_state.copy_ativa}\n\n🛒 COMPRE AQUI: {link_final}", height=150)
        
        st.divider()
        st.markdown("#### ⚙️ Motor de Queima de Vídeo (Automático)")
        
        # Pastas do seu PC
        pasta_entrada = r"C:\videos_antigos"
        pasta_saida = r"C:\ia_video"
        video_base = os.path.join(pasta_entrada, "video_modelo_nexus.mp4")
        
        if st.button("🎞️ INICIAR EDIÇÃO DE ALTA RETENÇÃO", type="primary"):
            with st.spinner("IA fatiando a copy e renderizando vídeo..."):
                
                # 1. A IA DIVIDE A COPY PARA A EDIÇÃO
                prompt_edicao = f"Divida esta copy em 3 partes curtas separadas por '|': [HOOK] | [DESEJO] | [CTA]. Copy: {st.session_state.copy_ativa}"
                
                try:
                    mapa_edicao = miny.minerar_produtos(prompt_edicao, "Shopee", motor_ia)
                    partes_texto = mapa_edicao.split('|')
                    
                    texto_hook = partes_texto[0].strip() if len(partes_texto) > 0 else "Olha isso!"
                    texto_meio = partes_texto[1].strip() if len(partes_texto) > 1 else st.session_state.copy_ativa
                    texto_cta = partes_texto[2].strip() if len(partes_texto) > 2 else "Link na Bio!"
                    
                    # 2. O MOVIEPY FAZ A MÁGICA (RENDERIZAÇÃO)
                    if os.path.exists(video_base):
                        # Carrega o vídeo original
                        video = VideoFileClip(video_base).subclip(0, 15) # Força 15 segundos
                        
                        # Cria os textos com design viral (Fonte grande, branca com borda preta)
                        # Nota: Exige configuração do ImageMagick no Windows para as fontes
                        txt_hook = TextClip(texto_hook, fontsize=50, color='white', stroke_color='black', stroke_width=2, method='caption', size=video.size).set_position('center').set_start(0).set_end(3)
                        
                        txt_meio = TextClip(texto_meio, fontsize=45, color='white', stroke_color='black', stroke_width=2, method='caption', size=video.size).set_position('center').set_start(3).set_end(10)
                        
                        txt_cta = TextClip(texto_cta, fontsize=55, color='yellow', stroke_color='black', stroke_width=3, method='caption', size=video.size).set_position('center').set_start(10).set_end(15)
                        
                        # Fundo tudo: Vídeo + Textos nos tempos certos
                        video_final = CompositeVideoClip([video, txt_hook, txt_meio, txt_cta])
                        
                        # Salva o resultado final na pasta de IA
                        caminho_final = os.path.join(pasta_saida, "reel_pronto_para_postar.mp4")
                        video_final.write_videofile(caminho_final, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        st.success(f"🚀 VÍDEO RENDERIZADO! Salvo em: {caminho_final}")
                        st.balloons()
                        st.session_state.copy_ativa = "" # Limpa para o próximo
                        
                    else:
                        st.error(f"Vídeo base não encontrado em: {video_base}")
                
                except Exception as e:
                    st.error(f"Erro no motor de renderização: {e}\n(Verifique se o MoviePy está instalado corretamente).")
    else:
        st.warning("⚠️ Volte no Arsenal, gere as copys e clique em 'Usar V1' para enviar o texto para a ilha de edição.")
