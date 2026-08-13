# 🔱 Manual Definitivo de Operação Autónoma do Nexus Bot

Este manual consolida todas as instruções necessárias para colocar o seu **Nexus Bot** a operar de forma 100% independente, desde a configuração das chaves de API até à entrega automática de links via ManyChat e agendamento na nuvem.

---

## 1. Configuração de Secrets no Streamlit Cloud

Para que a sua aplicação web tenha acesso às IAs e às ferramentas de postagem sem expor dados sensíveis, as chaves devem ser configuradas diretamente no painel do Streamlit Cloud.

1. Aceda ao seu painel no [Streamlit Cloud](https://share.streamlit.io/).
2. Localize o projeto `nexus-bot`, clique nos três pontos (`...`) e selecione **Settings**.
3. No menu lateral, clique em **Secrets**.
4. Insira as suas chaves no formato TOML exato abaixo e clique em **Save**:

```toml
NEXUS_PASSWORD = "sua_senha_segura"
OPENAI_API_KEY = "sk-proj-sua-chave-openai-aqui"
GROQ_API_KEY = "gsk_sua-chave-groq-aqui"
PINTEREST_ACCESS_TOKEN = "puna_seu_token_do_pinterest_aqui"
ML_AFFILIATE_ID = "ML_BR_12345"
```

---

## 2. Automação Diária e Agendamento (GitHub Actions)

Para que o bot execute ciclos de mineração e crie conteúdo sozinho todos os dias sem precisar do seu computador ligado:

1. No seu repositório no GitHub (`henriquetrader281-pixel/nexus-bot`), clique em **Add file** > **Create new file**.
2. Defina o caminho e o nome do ficheiro exatamente como: `.github/workflows/nexus_daily.yml`
3. Cole o seguinte código de automação:

```yaml
name: Nexus Daily Autonomous Pipeline

on:
  schedule:
    - cron: '0 9,18 * * *' # Executa todos os dias às 09:00 e 18:00 UTC
  workflow_dispatch: # Botão manual de 1 clique

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

4. Clique em **Commit changes**.
5. Vá a **Settings > Secrets and variables > Actions** no GitHub e insira as mesmas chaves (`OPENAI_API_KEY`, `PINTEREST_ACCESS_TOKEN`, etc.) para que a nuvem consiga lê-las.

---

## 3. Integração com ManyChat (Entrega Automática de Links via DM)

A estratégia de maior conversão para afiliados no Instagram e TikTok baseia-se em não colocar o link na legenda (para evitar bloqueios de alcance), mas sim utilizar o gatilho de comentários com o **ManyChat**.

### Passo a Passo no ManyChat:
1. Crie uma conta gratuita no [ManyChat](https://manychat.com/) e conecte a sua conta profissional do Instagram.
2. Vá ao menu **Automation** > **New Automation**.
3. Escolha o gatilho **User Comments on Your Post/Reels**.
4. Defina a regra: *Quando um utilizador comentar qualquer publicação com a palavra-passe:* **`QUERO`**.
5. Configure a Ação (Send Message) com a seguinte estrutura humanizada gerada pelo Nexus Bot:
   > *"Olá! Que bom que gostaste do achado. Conforme prometido, aqui está o link direto com desconto exclusivo para garantires o teu: [INSERIR_LINK_DE_AFILIADO_MERCADO_LIVRE_OU_SHOPEE]"*
6. Ative a automação. 

Assim, quando o seu vídeo (gerado na Fábrica de Vídeos do Nexus) for publicado e o agendador disparar, cada comentário "QUERO" ativará o ManyChat instantaneamente, enviando o link de afiliado por mensagem privada sem exigir qualquer esforço manual.
