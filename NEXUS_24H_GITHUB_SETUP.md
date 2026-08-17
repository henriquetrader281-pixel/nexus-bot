# Ativação do Nexus 24h no GitHub Actions

O código do Nexus já está no branch `main`. O workflow não foi criado automaticamente dentro de `.github/workflows/` porque o token GitHub utilizado nesta sessão não possui a permissão `workflows`. Para ativar a execução agendada, crie o ficheiro abaixo diretamente na interface do GitHub.

## 1. Criar o workflow pela interface do GitHub

Abra o repositório [henriquetrader281-pixel/nexus-bot](https://github.com/henriquetrader281-pixel/nexus-bot), entre em **Add file → Create new file**, escreva o caminho `.github/workflows/nexus_24h.yml` e cole exatamente este conteúdo:

```yaml
name: Nexus 24h Affiliate Cycle

on:
  workflow_dispatch:
  schedule:
    - cron: "0 */6 * * *"

permissions:
  contents: read

jobs:
  nexus-cycle:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout do código
        uses: actions/checkout@v4

      - name: Configurar Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Instalar dependências
        run: python -m pip install --upgrade pip && pip install -r requirements.txt

      - name: Executar ciclo autónomo
        env:
          ML_TRACKING_ID: ${{ secrets.ML_TRACKING_ID }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}
          PINTEREST_BOARD_ID: ${{ secrets.PINTEREST_BOARD_ID }}
          MANYCHAT_WEBHOOK_URL: ${{ secrets.MANYCHAT_WEBHOOK_URL }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          INSTAGRAM_BUSINESS_ACCOUNT_ID: ${{ secrets.INSTAGRAM_BUSINESS_ACCOUNT_ID }}
          TIKTOK_ACCESS_TOKEN: ${{ secrets.TIKTOK_ACCESS_TOKEN }}
          SHOPEE_TRACKING_ID: ${{ secrets.SHOPEE_TRACKING_ID }}
          AMAZON_TRACKING_ID: ${{ secrets.AMAZON_TRACKING_ID }}
        run: python worker.py
```

Clique em **Commit changes** e confirme no branch `main`. Depois abra o separador **Actions**, selecione **Nexus 24h Affiliate Cycle** e use **Run workflow** para executar o primeiro teste manual. O agendamento está definido para cada seis horas, usando o horário UTC do GitHub; se preferir uma única execução diária, substitua a linha `0 */6 * * *` por `0 12 * * *`.

## 2. Criar os Secrets

No repositório, abra **Settings → Secrets and variables → Actions → New repository secret**. Crie cada nome abaixo exatamente como aparece. Nunca coloque estes valores no código, no HTML de prévia, numa issue ou num commit público.

| Secret | Obrigatório para | Valor esperado |
|---|---|---|
| `ML_TRACKING_ID` | Identificação do afiliado Mercado Livre | O identificador confirmado no Portal do Afiliado |
| `GEMINI_API_KEY` | Mineração e análise com Gemini | Chave da API Gemini |
| `GROQ_API_KEY` | Geração rápida de copy | Chave da API Groq |
| `PINTEREST_ACCESS_TOKEN` | Publicação de Pins | Token da API Pinterest |
| `PINTEREST_BOARD_ID` | Destino dos Pins | ID numérico/string do board autorizado |
| `MANYCHAT_WEBHOOK_URL` | Entrega do link por DM | URL HTTPS do webhook/fluxo ManyChat ou Make |
| `ELEVENLABS_API_KEY` | Voz profissional | Opcional; sem ele o fallback configurado é utilizado |
| `OPENAI_API_KEY` | Motores que dependam de OpenAI | Opcional conforme o provedor escolhido |
| `INSTAGRAM_ACCESS_TOKEN` | Reels via Graph API | Opcional até a conta Business estar validada |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Reels via Graph API | Opcional e complementar ao token Instagram |
| `TIKTOK_ACCESS_TOKEN` | Content Posting API | Opcional até a aplicação TikTok ser aprovada |
| `SHOPEE_TRACKING_ID` | Campanhas Shopee | Opcional |
| `AMAZON_TRACKING_ID` | Campanhas Amazon | Opcional |

## 3. Link oficial do Mercado Livre

No campo da campanha, cole o link gerado dentro do Portal do Afiliado, normalmente no formato `https://meli.la/...`. O Nexus preserva esse link como recebido. Não substitua o URL por um link de produto comum nem acrescente manualmente parâmetros `matt_word`, `matt_tool` ou `ref`; esses dados devem vir do próprio Portal do Afiliado.

## 4. Validação sem publicar

Antes do primeiro disparo real, execute localmente ou no ambiente de teste:

```bash
python validate_social_credentials.py --json
python test_metrics_store.py
python -m py_compile worker.py autonomo_engine.py postador.py generate_creatives.py metrics_store.py
```

O validador não envia uma DM por padrão. A opção `--send-manychat-test` deve ser usada apenas quando o webhook estiver configurado para aceitar um evento técnico de teste.

## 5. O que o workflow executa

Cada execução chama `worker.py`, que prepara o estado headless, executa o ciclo mestre, minera um produto, gera a copy, aciona o webhook ManyChat, tenta publicar no Pinterest quando os dois Secrets do Pinterest existem, chama a supervisão Hermes e regista a publicação real no SQLite de métricas. A Imagem A e o Vídeo B também podem ser gerados localmente com `generate_creatives.py`; a publicação automática continua condicionada à existência de um token e de um destino público válido para cada rede.

> O workflow não confirma vendas automaticamente. CTR, cliques e conversões só se tornam dados reais quando as APIs ou exports das plataformas fornecerem esses eventos; o banco não inventa métricas.

## Referências

[1]: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule "GitHub Docs — Events that trigger workflows: schedule"
[2]: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions "GitHub Docs — Using secrets in GitHub Actions"
[3]: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions "GitHub Docs — Workflow syntax for GitHub Actions"
