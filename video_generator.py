import os
try:
    from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy import ImageClip, ColorClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import random

def criar_reels_elite(image_urls, audio_path=None, output_path="reels_final.mp4"):
    """
    Gera um Reels de alta retenção com múltiplos cortes (cenas) e trilha sonora.
    """
    try:
        width, height = 1080, 1920
        clips = []
        
        # 1. Lógica de Cortes (Cenas de 1.5 a 2 segundos cada para alta retenção)
        for i, url in enumerate(image_urls):
            # No mundo real, aqui baixaríamos a imagem. Aqui simulamos o clip.
            # Criamos um efeito de zoom diferente para cada cena (Cortes nível agência)
            duracao_cena = 1.5 if i == 0 else 2.0 # Gancho inicial mais rápido
            
            # Simulamos o clip de imagem (usando a imagem sincronizada)
            clip = ImageClip(url).with_duration(duracao_cena)
            
            # Alternar efeitos de zoom para cada corte
            if i % 2 == 0:
                clip = clip.resized(lambda t: 1 + 0.08 * t).with_position('center') # Zoom In
            else:
                clip = clip.resized(lambda t: 1.2 - 0.05 * t).with_position('center') # Zoom Out
                
            clips.append(clip)
            
        # 2. Montagem Final (Cortes Secos para ritmo)
        video_final = concatenate_videoclips(clips, method="compose")
        
        # 3. Integração de Áudio (Músicas em Alta)
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path).with_duration(video_final.duration)
            video_final = video_final.with_audio(audio)
            
        # 4. Exportação Profissional
        video_final.write_videofile(output_path, fps=30, codec='libx264', audio=True if audio_path else False)
        return output_path
        
    except Exception as e:
        print(f"Erro no Estúdio de Elite: {e}")
        return None

def obter_musica_tendencia(estilo="viral"):
    """
    Simula a seleção de uma música que está em alta no dia.
    """
    trilhas = {
        "viral": "lofi_beats_trending.mp3",
        "agressivo": "fast_phonk_high_retention.mp3",
        "estético": "minimalist_luxury_vibe.mp3"
    }
    return trilhas.get(estilo, "default_trend.mp3")
