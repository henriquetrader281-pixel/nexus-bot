# 💬 Guia de Configuração: Webhook Automático ManyChat

Para que o **Nexus Bot** envie automaticamente os dados do produto e o link de afiliado para o ManyChat assim que o ciclo for concluído, siga estes passos:

---

### Passo 1: Obter o URL do Webhook no ManyChat
1. Aceda ao seu painel do [ManyChat](https://manychat.com/).
2. Vá ao menu **Settings** > **API & Integrations** (ou crie um novo fluxo de Automação).
3. Selecione a opção de gatilho por **External Request (Webhook)** ou crie um fluxo de entrada de dados via API.
4. Copie o URL único fornecido pelo ManyChat (ex: `https://app.manychat.com/fb/api/v2/your_webhook_url`).

---

### Passo 2: Configurar a Secret no Streamlit Cloud
1. No seu painel do Streamlit Cloud, vá ao seu projeto `nexus-bot` > **Settings** > **Secrets**.
2. Adicione a seguinte linha no formato TOML:
   ```toml
   MANYCHAT_WEBHOOK_URL = "https://app.manychat.com/fb/api/v2/your_webhook_url"
   ```
3. Clique em **Save**.

---

### Passo 3: Testar a Automação
* Quando clicar em **🚀 ATIVAR AGENTE AGORA (1 CLIQUE)** na aba inicial do Nexus Bot, o Passo 4 enviará automaticamente um pacote JSON (`POST`) contendo:
  - `produto`: Nome do produto validado.
  - `link_afiliado`: Link direto de afiliado do Mercado Livre, Shopee ou Amazon.
  - `copy`: Texto de alta conversão gerado pela IA.
  - `trigger`: Palavra-passe "QUERO".
* O ManyChat receberá estes dados instantaneamente e poderá disparar a mensagem privada (DM) para o seguidor que comentou na publicação!
