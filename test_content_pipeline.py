import sys
import types

import content_pipeline


class FakeState:
    def __init__(self, initial):
        self.data = dict(initial)

    def set_campaign(self, **updates):
        self.data.update(updates)
        return dict(self.data)

    def get_campaign(self):
        return dict(self.data)


def install_fakes(monkeypatch, *, media_error=None, voice=None, queue_id=17):
    state = FakeState({"product_name": "Power Bank 10000mah", "pain": "ficar sem bateria"})
    calls = {"analysis": 0, "copy": 0, "voice": 0, "media": 0, "queue": 0}

    def analysis(*args):
        calls["analysis"] += 1
        return {
            "hooks": ["Você ainda fica sem bateria?"],
            "keywords": ["power bank", "bateria externa"],
            "caption": "Confira a oferta oficial.",
            "cta_variations": ["Comente QUERO"],
            "intent": "dor_imediata",
            "intent_label": "problema imediato",
        }

    def copy(campaign, result):
        calls["copy"] += 1
        return "Você ainda fica sem bateria? Comente QUERO.", "fallback local"

    def voice_fn(text):
        calls["voice"] += 1
        if isinstance(voice, Exception):
            raise voice
        return voice or {"success": True, "audio_path": ".nexus_media/audio/test.mp3"}

    def media(campaign, *, output_root):
        calls["media"] += 1
        if media_error:
            raise media_error
        return {
            "source_image_path": "source.jpg",
            "image_a": "image.jpg",
            "video_b": "video.mp4",
            "product": {"image_url": "https://cdn.example/image.jpg"},
        }

    def save(campaign, *, status):
        calls["queue"] += 1
        assert campaign["copy_final"]
        assert status in {"ready", "needs_review"}
        return queue_id

    monkeypatch.setattr(content_pipeline.campaign_state, "get_campaign", state.get_campaign)
    monkeypatch.setattr(content_pipeline.campaign_state, "set_campaign", state.set_campaign)
    monkeypatch.setattr(content_pipeline, "analisar_palavras_chave", analysis)
    monkeypatch.setattr(content_pipeline, "gerar_copy", copy)
    monkeypatch.setattr(content_pipeline, "generate_campaign_media", media)
    monkeypatch.setattr(content_pipeline.campaign_queue, "save_prepared_campaign", save)
    monkeypatch.setitem(sys.modules, "tts_engine", types.SimpleNamespace(gerar_narração_ia=voice_fn))
    return state, calls


def test_missing_product_is_blocked_without_side_effects(monkeypatch):
    result = content_pipeline.generate_campaign_package({"pain": "sem produto"}, save_queue=True)
    assert result.status == "blocked"
    assert result.ready is False
    assert result.errors == ["Nenhum produto foi selecionado para a campanha."]


def test_success_runs_all_stages_and_saves_queue(monkeypatch, tmp_path):
    state, calls = install_fakes(monkeypatch)
    result = content_pipeline.generate_campaign_package(state.data, output_root=tmp_path)

    assert result.status == "ready"
    assert result.ready is True
    assert result.queue_id == 17
    assert result.manifest["video_b"] == "video.mp4"
    assert result.campaign["audio_path"].endswith("test.mp3")
    assert calls == {"analysis": 1, "copy": 1, "voice": 1, "media": 1, "queue": 1}
    assert result.warnings == ["fallback local"]


def test_audio_failure_is_non_blocking(monkeypatch, tmp_path):
    state, calls = install_fakes(monkeypatch, voice=RuntimeError("ElevenLabs indisponível"))
    result = content_pipeline.generate_campaign_package(state.data, output_root=tmp_path)

    assert result.status == "ready"
    assert result.errors == []
    assert any("Áudio indisponível" in warning for warning in result.warnings)
    assert calls["media"] == 1


def test_media_failure_requires_review_and_still_queues(monkeypatch, tmp_path):
    state, calls = install_fakes(monkeypatch, media_error=RuntimeError("imagem ausente"))
    result = content_pipeline.generate_campaign_package(state.data, output_root=tmp_path)

    assert result.status == "needs_review"
    assert result.ready is False
    assert result.manifest is None
    assert result.errors == ["Mídia não gerada: imagem ausente"]
    assert calls["queue"] == 1


def test_copy_failure_is_blocking(monkeypatch):
    state, calls = install_fakes(monkeypatch)
    monkeypatch.setattr(content_pipeline, "gerar_copy", lambda campaign, analysis: (_ for _ in ()).throw(RuntimeError("modelo indisponível")))
    result = content_pipeline.generate_campaign_package(state.data)

    assert result.status == "blocked"
    assert result.errors == ["Não foi possível gerar a copy: modelo indisponível"]
    assert calls["voice"] == 0
    assert calls["media"] == 0
    assert calls["queue"] == 0


def test_analysis_failure_is_blocking(monkeypatch):
    state, calls = install_fakes(monkeypatch)
    monkeypatch.setattr(content_pipeline, "analisar_palavras_chave", lambda *args: (_ for _ in ()).throw(RuntimeError("análise indisponível")))
    result = content_pipeline.generate_campaign_package(state.data)

    assert result.status == "blocked"
    assert "análise indisponível" in str(result.errors)
    assert calls["copy"] == 0
    assert calls["media"] == 0
    assert calls["queue"] == 0


def test_queue_can_be_disabled_for_dry_run(monkeypatch, tmp_path):
    state, calls = install_fakes(monkeypatch)
    result = content_pipeline.generate_campaign_package(state.data, output_root=tmp_path, save_queue=False)

    assert result.status == "ready"
    assert result.queue_id is None
    assert calls["queue"] == 0
