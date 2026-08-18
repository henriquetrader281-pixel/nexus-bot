from pathlib import Path

source = Path("autonomo_engine.py").read_text(encoding="utf-8")
assert "MINERAR → COPY → ÁUDIO → IMAGEM → VÍDEO → GUARDAR" in source
assert 'dados_base = obter_produto_real_validado("gemini")' not in source
assert "executar_ciclo_mestre_um_clique(provedor=\"gemini\", publicar=False)" in source
assert "queue_status" in source
assert "manual_only" in source

print("SEQUENTIAL_FLOW_TEST_OK")
