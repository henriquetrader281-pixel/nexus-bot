import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def processar_video_viral(video_path, texto_copy, output_name="video_final.mp4"):
    try:
        # 1. Carrega o vídeo original (baixado da Shopee)
        clip = VideoFileClip(video_path).subclip(0, 15) # Limita a 15s para Reels
        w, h = clip.size

        # 2. Cria uma tarja preta semi-transparente para o texto não "sumir" no fundo
        # Colocamos no fundo do vídeo (estilo legenda de filme)
        tarja = ColorClip(size=(w, h // 4), color=(0,0,0)).set_opacity(0.6)
        tarja = tarja.set_duration(clip.duration).set_position(('center', 'bottom'))

        # 3. Cria o Texto da Copy (Atenção: Requer ImageMagick no servidor)
        # Escolhemos uma fonte impactante e cor branca
        texto = TextClip(
            texto_copy, 
            fontsize=30, 
            color='white', 
            font='Arial-Bold',
            method='caption',
            size=(w * 0.8, None)
        ).set_duration(clip.duration).set_position(('center', h - (h // 5)))

        # 4. Faz a "Montagem" das camadas
        video_final = CompositeVideoClip([clip, tarja, texto])

        # 5. Renderiza o ficheiro final
        video_final.write_videofile(output_name, fps=24, codec="libx264")
        
        return output_name
    except Exception as e:
        st.error(f"Erro na renderização: {e}")
        return None
