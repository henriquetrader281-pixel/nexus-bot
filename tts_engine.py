import streamlit as st
from gtts import gTTS
import os
import random

def gerar_narração_ia(texto_roteiro, estilo="Normal"):
    """
    Gera narração de voz real usando gTTS.
    """
    try:
        if not texto_roteiro:
            texto_roteiro = "Confira este produto incrível no link da bio!"
            
        # Limpa o texto de tags e lixo
        texto_limpo = texto_roteiro.split('###')[0].strip()
        
        # Gera o áudio
        tts = gTTS(text=texto_limpo, lang='pt', tld='com.br')
        output_path = "narração_nexus.mp3"
        tts.save(output_path)
        
        return {
            "voz": "Google AI (Brasil)",
            "estilo": estilo,
            "status": "Áudio Real Gerado",
            "audio_path": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def obter_audio_tendencia():
    trends = [
        {"nome": "Luxury Aesthetic (Trending)", "bpm": 128, "uso": "High Retention"},
        {"nome": "Phonk Viral 2026", "bpm": 140, "uso": "Dynamic Cuts"},
        {"nome": "Lo-Fi Study Beats", "bpm": 90, "uso": "Product Review"}
    ]
    return random.choice(trends)

def exibir_painel_voz():
    st.markdown("#### 🎙️ Narração IA Real & Áudio Viral")
    
    c1, c2 = st.columns(2)
    
    with c1:
        voz = st.selectbox("Motor de Voz:", ["Google AI (Brasil)", "ElevenLabs (Requer API)"])
        estilo = st.select_slider("Energia da Voz:", options=["Calmo", "Normal", "Energético"])
        
    with c2:
        trend = obter_audio_tendencia()
        st.success(f"🎵 **Trend:** {trend['nome']}")
        st.caption(f"BPM: {trend['bpm']} | Ideal para: {trend['uso']}")
        
    if st.button("🔊 GERAR NARRAÇÃO REAL", use_container_width=True):
        with st.spinner("Sintetizando voz humana..."):
            roteiro = st.session_state.get('copy_ativa', "Garanta já o seu com envio full!")
            resultado = gerar_narração_ia(roteiro, estilo)
            
            if "audio_path" in resultado:
                st.session_state.audio_pronto = resultado
                st.audio(resultado['audio_path'])
                st.success("✅ Áudio gerado e pronto para o vídeo!")
            else:
                st.error(f"Erro na geração: {resultado.get('error')}")
