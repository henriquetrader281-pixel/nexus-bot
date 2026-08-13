# 💰 Arquitetura do Funil de Vendas Completo (Nexus Bot)

Este documento detalha o funcionamento cirúrgico do funil de vendas automatizado pelo **Nexus Bot**, combinando a captação no Pinterest/Instagram, a automação de DMs no ManyChat e a monetização via Mercado Livre e Shopee.

---

## 🗺️ O Fluxo do Funil de Ponta a Ponta

```text
[ 1. Mineração IA (Gemini/OpenAI) ] 
                 ↓
[ 2. Geração de Mídia com Hook & AIDA ] 
                 ↓
[ 3. Postagem Automática (Pinterest API / Scheduler) ] 
                 ↓
[ 4. Captação de Lead com "Comenta QUERO" ] 
                 ↓
[ 5. ManyChat DM Automática com Link de Afiliado ] 
                 ↓
[ 6. Checkout Mercado Livre / Shopee (Comissão Gerada 💰) ]
```

---

## 🛠️ Passo a Passo para Configurar o Ecossistema

### 1. Configuração de Secrets no Streamlit Cloud
Para que o bot utilize as IAs (OpenAI, Gemini, Groq) e a API do Pinterest sem expor credenciais, configure no painel do Streamlit (`Settings > Secrets`):

```toml
NEXUS_PASSWORD = "sua_senha_segura"
OPENAI_API_KEY = "sk-proj-..."
GEMINI_API_KEY = "AIzaSy..."
GROQ_API_KEY = "gsk_..."
PINTEREST_ACCESS_TOKEN = "puna_token_aqui"
ML_AFFILIATE_ID = "ML_BR_12345"
```

### 2. Atração (Pinterest & Instagram Reels)
* O **Nexus Bot** utiliza o **Google Trends** e a **Espionagem Global** para detetar o produto vencedor.
* O motor de IA (Gemini ou GPT-4o) gera um **Hook de 3 Segundos** (gancho para parar o scroll) e uma copy baseada no framework **AIDA**.
* A imagem ou vídeo é gerada automaticamente com efeitos de retenção e publicada no **Pinterest** via API ou agendada pelo **Scheduler**.

### 3. Engajamento e Conversão no ManyChat
* Na legenda do Pin ou Reels gerado pelo bot, o CTA é sempre o mesmo: *"Cansada de [Dor]? Comenta **QUERO** que te envio o segredo no direct!"*.
* O **ManyChat** monitoriza os comentários do seu Instagram. Assim que alguém comenta "QUERO", o ManyChat dispara uma mensagem privada (DM) instantânea.

### 4. O Fechamento (Mercado Livre Afiliado)
* Na DM do ManyChat, o lead recebe o link gerado pelo Nexus Bot (ex: o link blindado do **Mercado Livre Afiliados** `_NoIndex_True` ou da **Shopee**).
* Como o link contém a sua tag de afiliado, qualquer compra realizada pelo cliente nas próximas 24 a 48 horas gera comissão direta na sua conta, de forma 100% passiva.
