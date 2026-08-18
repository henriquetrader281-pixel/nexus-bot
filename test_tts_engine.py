import sys
import tempfile
import types
from pathlib import Path


class FakeSecrets(dict):
    pass


fake_streamlit = types.ModuleType("streamlit")
fake_streamlit.secrets = FakeSecrets()
sys.modules["streamlit"] = fake_streamlit

fake_gtts = types.ModuleType("gtts")


class FakeTTS:
    def __init__(self, text, lang, tld):
        self.text = text

    def save(self, path):
        Path(path).write_bytes(b"fake audio")


fake_gtts.gTTS = FakeTTS
sys.modules["gtts"] = fake_gtts

import tts_engine

with tempfile.TemporaryDirectory() as temp_dir:
    tts_engine._audio_path = lambda professional: Path(temp_dir) / "voice.mp3"
    result = tts_engine.gerar_narração_ia("Gancho do produto. Comente QUERO.")
    assert result["success"] is True
    assert Path(result["audio_path"]).is_file()
print("TTS_ENGINE_TEST_OK")
