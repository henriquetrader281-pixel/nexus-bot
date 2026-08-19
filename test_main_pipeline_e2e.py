from pathlib import Path
import tempfile
import wave

import campaign_queue
import campaign_state
import nexus_pipeline_ui as main_ui


def make_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 8000)


# Isola o teste de uma sessão Streamlit anterior.
campaign_state.clear_campaign()

product = {
    "produto": "Power Bank 10000mah Carregador Portátil",
    "product_name": "Power Bank 10000mah Carregador Portátil",
    "product_source_url": "https://www.mercadolivre.com.br/power-bank-e2e/p/MLB-E2E",
    "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_E2E.jpg",
    "image_verified": True,
    "image_source": "thumbnail do anúncio",
    "marketplace": "Mercado Livre",
    "price": 99.90,
}

main_ui._apply_mined_product(product, "power bank", "Teste comercial")
campaign = campaign_state.get_campaign()
assert campaign["product_name"] == product["product_name"]
assert "bateria" in campaign["pain"].lower()
assert campaign["trend_term"] == "power bank"
assert campaign["image_url"] == product["image_url"]
assert campaign["keywords"]

with tempfile.TemporaryDirectory(prefix="nexus_main_e2e_") as tmp:
    tmp_path = Path(tmp)
    audio_path = tmp_path / "voice.wav"
    make_wav(audio_path)

    original_voice = None
    original_media = main_ui.generate_campaign_media
    original_save = main_ui.campaign_queue.save_prepared_campaign
    try:
        import tts_engine
        original_voice = tts_engine.gerar_narração_ia
        tts_engine.gerar_narração_ia = lambda _text: {"success": True, "audio_path": str(audio_path)}

        from media_pipeline import generate_campaign_media as real_media
        main_ui.generate_campaign_media = lambda data: real_media(data, output_root=tmp_path / "media")
        main_ui.campaign_queue.save_prepared_campaign = lambda data, status="ready": 9001
        generated, status = main_ui._generate_package(campaign)
    finally:
        if original_voice is not None:
            tts_engine.gerar_narração_ia = original_voice
        main_ui.generate_campaign_media = original_media
        main_ui.campaign_queue.save_prepared_campaign = original_save

    assert status == "ready", status
    assert generated["queue_id"] == 9001
    assert generated["copy_final"]
    assert generated["caption"]
    assert generated["audio_path"] == str(audio_path)
    assert Path(generated["image_path"]).is_file()
    assert Path(generated["video_path"]).is_file()
    assert generated["media_manifest"]["publication"] == "not_executed"

print("MAIN_PIPELINE_E2E_OK")
