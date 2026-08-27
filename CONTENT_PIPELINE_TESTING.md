# Testes do `content_pipeline.py`

O serviço consolidado é testado sem chamadas reais ao Mercado Livre, Groq, ElevenLabs, gTTS, MoviePy ou banco de produção. Os testes substituem as bordas externas por funções controladas e verificam apenas a orquestração do pipeline.

## Cenários cobertos

| Cenário | Comportamento esperado |
|---|---|
| Produto ausente | Retorna `blocked`, informa o erro e não grava na fila. |
| Execução completa | Analisa, gera copy, tenta voz, cria mídia e grava uma campanha `ready`. |
| Voz indisponível | Adiciona aviso, mas continua a geração de mídia. |
| Mídia indisponível | Retorna `needs_review`, preserva o erro e ainda registra o pacote para revisão. |
| `save_queue=False` | Executa em modo dry-run sem gravar na fila. |

## Execução

Na raiz do projeto:

```bash
python3 -m pytest -q test_content_pipeline.py
```

Para executar também os testes de autenticação e cache de mídia:

```bash
python3 -m pytest -q \
  test_content_pipeline.py \
  test_auth.py \
  test_media_pipeline_cache.py
```

A suíte usa `monkeypatch` para substituir `campaign_state`, `campaign_queue`, análise, copy, voz e mídia. Assim, os testes são rápidos, reproduzíveis e não consomem créditos nem alteram contas externas.

## Integração futura nas interfaces

Depois que a suíte estiver estável, `nexus_pipeline_ui.py` e `simple_mode.py` devem chamar somente:

```python
from content_pipeline import generate_campaign_package

result = generate_campaign_package(campaign)
```

A interface pode renderizar `result.warnings`, `result.errors`, `result.status` e `result.manifest`, sem duplicar a lógica de geração. A migração deve ocorrer depois dos testes, em uma alteração separada, para facilitar rollback.
