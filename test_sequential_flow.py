from pathlib import Path

source = Path("autonomo_engine.py").read_text(encoding="utf-8")
main_source = Path("nexus_pipeline_ui.py").read_text(encoding="utf-8")
assert "MINERAR → COPY → ÁUDIO → IMAGEM → VÍDEO → GUARDAR" in source
assert 'dados_base = obter_produto_real_validado("gemini")' not in source
assert "executar_ciclo_mestre_um_clique(provedor=\"gemini\", publicar=False)" in source
assert "queue_status" in source
assert "manual_only" in source
assert "main_pending_query" in main_source
assert "st.session_state.main_search_query = trend_term" not in main_source

print("SEQUENTIAL_FLOW_TEST_OK")
