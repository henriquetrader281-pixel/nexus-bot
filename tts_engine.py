import streamlit as st
import random

def gerar_narração_ia(texto_roteiro, estilo="Motivacional"):
    """
    Simula a geração de narração de voz IA (ElevenLabs/Google TTS style)
    """
    vozes = ["Felipe (Grave/Vendas)", "Julia (Entusiasta)", "Ricardo (Narrador Doc)", "Sofia (Suave/Zen)"]
    voz_escolhida = random.choice(vozes)
    
    # Simulação de processamento
    return {
        "voz": voz_escolhida,
        "estilo": estilo,
        "status": "Áudio Gerado com Sucesso",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # Placeholder de áudio
    }

def obter_audio_tendencia():
    """
    Retorna áudios que estão em alta no Instagram/TikTok
    """
    trends = [
        {"nome": "Luxury Aesthetic (Trending)", "bpm": 128, "uso": "High Retention"},
        {"nome": "Phonk Viral 2026", "bpm": 140, "uso": "Dynamic Cuts"},
        {"nome": "Lo-Fi Study Beats", "bpm": 90, "uso": "Product Review"},
        {"nome": "Fast & Furious Remix", "bpm": 135, "uso": "Flash Sales"}
    ]
    return random.choice(trends)

def exibir_painel_voz():
    st.markdown("#### 🎙️ Narração IA & Áudio Viral")
    
    c1, c2 = st.columns(2)
    
    with c1:
        voz = st.selectbox("Escolha a Voz da IA:", ["Felipe (Vendas)", "Julia (Desejo)", "Ricardo (Autoridade)", "Sofia (Suave)"])
        estilo = st.select_slider("Estilo da Narração:", options=["Calmo", "Normal", "Energético", "Agressivo"])
        
    with c2:
        trend = obter_audio_tendencia()
        st.success(f"🎵 **Trend Detectada:** {trend['nome']}")
        st.caption(f"Recomendado para: {trend['uso']} | BPM: {trend['bpm']}")
        
    if st.button("🔊 GERAR NARRAÇÃO & SINCRONIZAR TREND", use_container_width=True):
        with st.spinner("Sincronizando áudio viral com narração IA..."):
            roteiro = st.session_state.get('micao_nexus', [""])[0]
            resultado = gerar_narração_ia(roteiro, estilo)
            st.session_state.audio_pronto = resultado
            st.audio(resultado['audio_url'])
            st.toast("Áudio e Narração prontos para o vídeo!")
