import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def criar_imagem_legenda(texto, largura, altura):
    # 1. Cria uma imagem transparente (RGBA)
    img = Image.new('RGBA', (largura, altura // 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Configura a fonte (O Streamlit já tem fontes padrão no Linux)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    # 3. Desenha uma tarja semi-transparente
    draw.rectangle([0, 0, largura, altura // 4], fill=(0, 0, 0, 160))
    
    # 4. Escreve o texto centralizado
    # Nota: O Pillow precisa de um ajuste manual de quebra de linha se o texto for longo
    draw.text((20, 20), texto, font=font, fill=(255, 255, 255, 255))
    
    return np.array(img)

def renderizar_reels_automatico(video_bruto_path, texto_copy):
    try:
        # Carrega o vídeo original
        clip = VideoFileClip(video_bruto_path).subclip(0, 15)
        w, h = clip.size

        # Gera a imagem da legenda usando Pillow
        img_array = criar_imagem_legenda(texto_copy, w, h)
        
        # Transforma a imagem em um clip de vídeo "parado"
        legenda_clip = ImageClip(img_array).set_duration(clip.duration).set_position(('center', 'bottom'))

        # Faz a fusão
        video_final = CompositeVideoClip([clip, legenda_clip])
        
        output_path = "reels_nexus_pronto.mp4"
        video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        return output_path
    except Exception as e:
        st.error(f"Erro na renderização: {e}")
        return None
