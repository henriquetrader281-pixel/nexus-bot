from pathlib import Path
import tempfile
import wave

import campaign_state
import nexus_pipeline_ui as main_ui

SOURCE_IMAGE = Path(".nexus_media/Power_Bank_10000mah_Carregador_Portátil_Turbo/source_product_image.jpg")
assert SOURCE_IMAGE.is_file(), f"Imagem-fonte de teste não encontrada: {SOURCE_IMAGE}"

campaign_state.clear_campaign()
campaign_state.set_campaign(
    product_name="Power Bank 10000mah Carregador Portátil",
    pain="ficar sem bateria quando precisa do celular e perder tempo procurando uma tomada",
    source_image_path=str(SOURCE_IMAGE),
    image_source="upload manual da imagem real do produto",
    image_verified=True,
    marketplace="Mercado Livre",
    source="manual_test",
    keywords=["power bank", "carregador portátil", "bateria externa"],
)


def make_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 8000)


# Mantém o teste independente de provedor de copy e de TTS.
original_analysis = main_ui.analisar_palavras_chave
original_copy = main_ui.gerar_copy
original_media = main_ui.generate_campaign_media
original_save = main_ui.campaign_queue.save_prepared_campaign
try:
    main_ui.analisar_palavras_chave = lambda *args, **kwargs: {
        "hooks": ["Chega de ficar procurando tomada quando mais precisa."],
        "keywords": ["power bank", "carregador portátil", "bateria externa"],
        "caption": "Mais autonomia para a sua rotina. Confira o produto e veja se faz sentido para você.",
        "cta_variations": ["Confira os detalhes"],
        "intent": "practical_problem",
        "intent_label": "Problema prático",
    }
    main_ui.gerar_copy = lambda campaign, analysis: (
        "Ficar sem bateria no meio da rotina é frustrante. Este power bank ajuda a manter o celular disponível quando você mais precisa. Confira os detalhes e avalie se ele serve para a sua rotina.",
        "Copy determinística do teste manual.",
    )

    import tts_engine
    original_voice = tts_engine.gerar_narração_ia
    with tempfile.TemporaryDirectory(prefix="nexus_manual_test_") as tmp:
        audio_path = Path(tmp) / "manual_voice.wav"
        make_wav(audio_path)
        tts_engine.gerar_narração_ia = lambda _text: {"success": True, "audio_path": str(audio_path)}

        from media_pipeline import generate_campaign_media as real_media
        main_ui.generate_campaign_media = lambda data: real_media(data, output_root=Path(tmp) / "media")
        main_ui.campaign_queue.save_prepared_campaign = lambda data, status="ready": 9101
        generated, status = main_ui._generate_package(campaign_state.get_campaign())

        assert status == "ready", status
        assert generated["product_name"].startswith("Power Bank")
        assert generated["pain"]
        assert generated["copy_final"]
        assert generated["caption"]
        assert Path(generated["audio_path"]).is_file()
        assert Path(generated["image_path"]).is_file()
        assert Path(generated["video_path"]).is_file()
        assert generated["publication_status"] == "manual_only"
finally:
    main_ui.analisar_palavras_chave = original_analysis
    main_ui.gerar_copy = original_copy
    main_ui.generate_campaign_media = original_media
    main_ui.campaign_queue.save_prepared_campaign = original_save
    tts_engine.gerar_narração_ia = original_voice

print("MANUAL_PIPELINE_TEST_OK")
