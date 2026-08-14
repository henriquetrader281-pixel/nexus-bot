# 📱 Guia Definitivo: Automação Social (TikTok, Instagram & Pinterest)

Este documento explica exatamente como configurar as publicações automáticas no TikTok e Instagram e como funcionam os links de afiliado no Pinterest.

---

## 1. Onde Colocar o Link de Afiliado no Pinterest?
No Pinterest, os Pins (imagens ou vídeos) possuem um campo obrigatório chamado **Destination Link** (Link de Destino). É exatamente para lá que o utilizador vai quando clica no seu Pin.

* **Como o Nexus Bot faz isso:** Quando o agente minera um produto, ele gera automaticamente o link blindado de afiliado (ex: Mercado Livre `_NoIndex_True`, Shopee ou Amazon). 
* **Na Prática:** Quando o bot faz a publicação automática via API no Pinterest, ele envia a imagem gerada, a copy persuasiva e insere o seu link de afiliado diretamente no campo de link de destino do Pin. Se preferir postar manualmente, basta copiar o link gerado na aba do Agente e colá-lo no campo "Link do site" ao criar o Pin no Pinterest.

---

## 2. Como Configurar a Publicação Automática no TikTok e Instagram?

Como o Instagram e o TikTok possuem restrições de segurança severas para logins diretos por scripts em Python, a **melhor prática de mercado** utilizada por agências é o uso de um Webhook integrado ao **Make.com** (ou Zapier).

### Passo a Passo da Automação (Make.com):
1. **Criar um Webhook no Make.com:**
   - Crie uma conta gratuita no [Make.com](https://www.make.com/).
   - Crie um novo cenário e adicione o módulo **Webhooks > Custom Webhook**.
   - Copie o URL gerado (ex: `https://hook.eu1.make.com/...`).

2. **Conectar ao Nexus Bot:**
   - No seu painel do Streamlit Cloud, vá a **Settings > Secrets** e adicione o URL do Make.com:
     ```toml
     MANYCHAT_WEBHOOK_URL = "https://hook.eu1.make.com/seu_codigo_aqui"
     ```
   - Assim que o Agente de 1-Clique rodar, ele enviará os dados (Vídeo, Copy, Link de Afiliado) para o Make.com.

3. **Distribuir para o Instagram Reels e TikTok:**
   - No Make.com, logo após o módulo Webhook, adicione o módulo **Instagram for Business > Create a Reel** (ou **TikTok > Upload a Video**).
   - Mapeie os campos recebidos do Nexus Bot:
     - *Video File:* URL do vídeo gerado no Estúdio.
     - *Caption:* Copy AIDA gerada pela IA + CTA.
   - Ative o cenário. A partir daí, cada clique no Agente do Nexus disparará o vídeo diretamente para as suas redes sociais no piloto automático!
