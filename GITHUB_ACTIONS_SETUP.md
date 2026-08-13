# 🚀 Guia de Configuração: Agendamento Diário Automático (GitHub Actions)

Para que o seu Nexus Bot execute totalmente sozinho todos os dias (gerando dores, produtos, copies e disparos), siga estes passos rápidos no seu repositório no GitHub:

1. Vá ao seu repositório: `https://github.com/henriquetrader281-pixel/nexus-bot`
2. Clique em **Add file** > **Create new file**.
3. No nome do ficheiro, escreva exatamente: `.github/workflows/nexus_daily.yml`
4. Cole o seguinte código lá dentro:

```yaml
name: Nexus Daily Autonomous Pipeline

on:
  schedule:
    - cron: '0 9,18 * * *' # Roda todos os dias às 09:00 e 18:00 UTC
  workflow_dispatch: # Permite rodar manualmente com 1 clique

jobs:
  run-nexus-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: |
          pip install openai groq requests pandas streamlit
      - name: Run Autonomous Engine
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}
          ML_AFFILIATE_ID: ${{ secrets.ML_AFFILIATE_ID }}
        run: |
          python nexus_autonome.py
```

5. Clique em **Commit changes**.
6. Vá a **Settings > Secrets and variables > Actions** e adicione as suas chaves (`OPENAI_API_KEY`, `PINTEREST_ACCESS_TOKEN`, `ML_AFFILIATE_ID`).

Pronto! O bot passará a rodar 100% autónomo na nuvem.
