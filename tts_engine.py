import streamlit as st
import requests
import os
import random

def gerar_narração_ia(texto_roteiro, estilo="Profissional"):
    """
    Gera narração de voz humana ultra-realista usando ElevenLabs.
    Se a chave API não estiver presente, faz fallback para gTTS com aviso.
    """
    api_key = st.secrets.get("ELEVENLABS_API_KEY")
    
    if not api_key:
        # Fallback para gTTS se não houver ElevenLabs configurado
        from gtts import gTTS
        try:
            tts = gTTS(text=texto_roteiro.split('###')[0], lang='pt', tld='com.br')
            output_path = "narração_nexus_basic.mp3"
            tts.save(output_path)
            return {"success": True, "audio_path": output_path, "aviso": "Usando voz básica. Configure ELEVENLABS_API_KEY para voz profissional."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Configuração ElevenLabs (Voz: Daniel - Narrador Profissional)
    voice_id = "onwK4e9ZLuTAKqWWpk49" 
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": texto_roteiro.split('###')[0],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            output_path = "narração_nexus_pro.mp3"
            with open(output_path, "wb") as f:
                f.write(response.content)
            return {"success": True, "audio_path": output_path}
        else:
            return {"success": False, "error": f"Erro ElevenLabs: {response.text}"}
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
    st.markdown("#### 🎙️ Narração IA Profissional (ElevenLabs)")
    
    if not st.secrets.get("ELEVENLABS_API_KEY"):
        st.warning("⚠️ **Voz Profissional Desativada:** Adicione `ELEVENLABS_API_KEY` nos Secrets para vozes humanas nível agência.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Motor de Voz:", ["ElevenLabs (Voz Humana)", "Google AI (Básico)"])
    with c2:
        trend = obter_audio_tendencia()
        st.success(f"🎵 **Trend:** {trend['nome']}")
        
    if st.button("🔊 GERAR NARRAÇÃO ELITE", use_container_width=True, type="primary"):
        with st.spinner("Sintetizando voz humana profissional..."):
            roteiro = st.session_state.get('copy_ativa', "Garanta já o seu com envio full!")
            resultado = gerar_narração_ia(roteiro)
            
            if resultado.get("success"):
                st.audio(resultado['audio_path'])
                st.success("✅ Áudio Profissional Gerado!")
                if "aviso" in resultado: st.info(resultado['aviso'])
            else:
                st.error(f"Erro: {resultado.get('error')}")
