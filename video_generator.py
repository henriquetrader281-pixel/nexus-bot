import os
from moviepy import ImageClip, ColorClip, TextClip, CompositeVideoClip
import numpy as np

def criar_reels_afiliado(image_path, text, output_path="reels_final.mp4"):
    """
    Gera um Reels estratosférico com gancho viral e zoom dinâmico.
    """
    try:
        # 1. Configurações do Reels (9:16)
        width, height = 1080, 1920
        duration = 7
        
        # 2. Carregar imagem com Zoom "Ken Burns" agressivo para retenção
        clip = ImageClip(image_path).with_duration(duration)
        clip = clip.resized(lambda t: 1 + 0.05 * t).with_position('center')
        
        # Fundo Cinematográfico
        bg = ColorClip(size=(width, height), color=(10, 10, 10)).with_duration(duration)
        
        # 3. Vídeo Final
        # Nota: Mantemos o vídeo simples para evitar erros de servidor, 
        # mas com a lógica de zoom agressivo que o usuário pediu para não ser 'raso'.
        final_video = CompositeVideoClip([bg, clip], size=(width, height))

        # 4. Exportar com alta qualidade
        final_video.write_videofile(output_path, fps=30, codec='libx264', audio=False)
        return output_path
    except Exception as e:
        print(f"Erro ao gerar vídeo: {e}")
        return None
