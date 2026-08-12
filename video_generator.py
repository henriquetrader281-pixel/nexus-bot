import os
from moviepy import ImageClip, ColorClip, TextClip, CompositeVideoClip
import numpy as np

def criar_reels_afiliado(image_path, text, output_path="reels_final.mp4"):
    try:
        # 1. Configurações do Reels (9:16)
        width, height = 1080, 1920
        duration = 7
        
        # 2. Carregar imagem
        clip = ImageClip(image_path).with_duration(duration)
        
        # Efeito de Zoom Lento
        clip = clip.resized(lambda t: 1 + 0.02 * t).with_position('center')
        
        # Fundo
        bg = ColorClip(size=(width, height), color=(0,0,0)).with_duration(duration)
        
        # 3. Vídeo Final (Sem texto por enquanto para evitar erro de ImageMagick no sandbox)
        final_video = CompositeVideoClip([bg, clip], size=(width, height))

        # 4. Exportar
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio=False)
        return output_path
    except Exception as e:
        print(f"Erro ao gerar vídeo: {e}")
        return None
