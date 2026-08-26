from __future__ import annotations

import hashlib
import os
from pathlib import Path

import requests
import streamlit as st

import campaign_state


def _secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name)


def _audio_path(professional: bool, text: str = "") -> Path:
    folder = Path(".nexus_media") / "audio"
    folder.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    prefix = "nexus_voice_pro" if professional else "nexus_voice_basic"
    return folder / f"{prefix}_{digest}.mp3"


def gerar_narração_ia(texto_roteiro, estilo="Profissional"):
    """Gera voz profissional ou usa gTTS como fallback, sem interromper a campanha."""
    text = str(texto_roteiro or "").split("###")[0].strip()
    if not text:
        return {"success": False, "error": "O roteiro de voz está vazio."}

    api_key = _secret("ELEVENLABS_API_KEY")
    if not api_key:
        try:
            from gtts import gTTS
            try:
                output_path = _audio_path(False, text)
            except TypeError:  # compatibilidade com integrações legadas/testes
                output_path = _audio_path(False)
            if output_path.is_file():
                return {"success": True, "audio_path": str(output_path), "aviso": "Narração reutilizada do cache local."}
            gTTS(text=text, lang="pt", tld="com.br").save(str(output_path))
            return {
                "success": True,
                "audio_path": str(output_path),
                "aviso": "Voz básica usada. Configure ELEVENLABS_API_KEY para voz profissional.",
            }
        except Exception as exc:
            return {"success": False, "error": f"Fallback gTTS indisponível: {exc}"}

    voice_id = "onwK4e9ZLuTAKqWWpk49"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": api_key}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.5, "use_speaker_boost": True},
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            try:
                output_path = _audio_path(True, text)
            except TypeError:  # compatibilidade com integrações legadas/testes
                output_path = _audio_path(True)
            if output_path.is_file():
                return {"success": True, "audio_path": str(output_path), "aviso": "Narração reutilizada do cache local."}
            output_path.write_bytes(response.content)
            return {"success": True, "audio_path": str(output_path)}
        return {"success": False, "error": f"Erro ElevenLabs HTTP {response.status_code}: {response.text[:300]}"}
    except requests.RequestException as exc:
        return {"success": False, "error": f"Falha de rede ElevenLabs: {exc}"}


def obter_audio_tendencia():
    return {"nome": "Narração original Nexus", "bpm": None, "uso": "Voz e legenda sincronizadas"}


def exibir_painel_voz():
    st.markdown("#### 🎙️ Narração IA Profissional (ElevenLabs)")
    if not _secret("ELEVENLABS_API_KEY"):
        st.warning("Configure ELEVENLABS_API_KEY para voz profissional; o fallback gTTS continua disponível.")
    if st.button("🔊 GERAR NARRAÇÃO ELITE", use_container_width=True, type="primary"):
        with st.spinner("Sintetizando voz..."):
            roteiro = campaign_state.get_campaign().get("copy_final") or "Garanta já o seu com oferta oficial."
            resultado = gerar_narração_ia(roteiro)
            if resultado.get("success"):
                campaign_state.set_campaign(audio_path=resultado["audio_path"])
                st.audio(resultado["audio_path"])
                st.success("Áudio gerado e anexado à campanha.")
                if resultado.get("aviso"):
                    st.info(resultado["aviso"])
            else:
                st.error(f"Erro: {resultado.get('error')}")
