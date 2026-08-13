# 🚀 Guia Técnico Avançado: Automação Total, SEO Pinterest e Webhook ManyChat

Este documento responde detalhadamente às três perguntas fundamentais para escalar o seu **Nexus Bot** rumo a uma operação profissional de afiliados.

---

## 1. Como criar o workflow no GitHub Actions para automatizar os disparos diários?

Como os tokens de aplicação do GitHub possuem restrições de segurança para escrita direta na pasta `.github/workflows` por agentes externos, a criação deve ser feita diretamente no seu navegador em menos de 1 minuto:

1. Aceda ao seu repositório: [https://github.com/henriquetrader281-pixel/nexus-bot](https://github.com/henriquetrader281-pixel/nexus-bot)
2. Clique no botão **Add file** (no canto superior direito da lista de ficheiros) e selecione **Create new file**.
3. No campo de nome do ficheiro, escreva exatamente:
   ```text
   .github/workflows/nexus_daily.yml
   ```
4. Cole o seguinte código robusto de automação no editor:

```yaml
name: Nexus Daily Autonomous Pipeline

on:
  schedule:
    - cron: '0 9,18 * * *' # Executa automaticamente todos os dias às 09:00 e 18:00 UTC
  workflow_dispatch: # Permite disparar manualmente com um clique a qualquer momento

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
          pip install openai groq requests pandas streamlit moviepy pillow imageio
      - name: Run Autonomous Engine
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}
          ML_AFFILIATE_ID: ${{ secrets.ML_AFFILIATE_ID }}
        run: |
          python nexus_autonome.py
```

5. Clique no botão verde **Commit changes...** no canto superior direito.
6. Vá a **Settings > Secrets and variables > Actions** no seu repositório e adicione as suas chaves de API (`OPENAI_API_KEY`, `PINTEREST_ACCESS_TOKEN`, etc.). A partir deste momento, o robô executará sozinho na nuvem nos horários programados.

---

## 2. Quais são as melhores estratégias de SEO e palavras-chave do Google Trends para usar nas copys do Pinterest?

O Pinterest não é uma rede social tradicional; **ele funciona como um motor de busca visual (um Google de imagens e ideias)**. Para dominar o tráfego orgânico e fazer vendas como afiliado:

### A. Estratégia de SEO Visual
* **Títulos Ricos em Palavras-Chave:** Em vez de dar títulos criativos aos seus Pins (ex: *Olha que legal isso!*), use termos que as pessoas realmente pesquisam (ex: *Organizador de Cozinha Compacto para Espaços Pequenos*).
* **Descrição com Cauda Longa (Long-Tail):** O Nexus Bot gera copies baseadas no framework AIDA, mas para o Pinterest o ideal é adicionar 3 a 5 hashtags estratégicas e termos de busca extraídos do [Google Trends Brasil](https://trends.google.com.br/trends/) [1].
* **Exemplo de Título Otimizado:** *"Achadinhos da Shopee: Como organizar a casa gastando pouco"*
* **Exemplo de Descrição SEO:** *"Cansada de perder tempo com a desorganização? Este organizador de escritório e cozinha resolve o problema em segundos. Clique no link para garantir o seu com desconto de afiliado!"*

### B. Uso do Google Trends na Geração de Conteúdo
1. Consulte periodicamente o [Google Trends](https://trends.google.com.br/trends/) para identificar picos sazonais (ex: Volta às Aulas, Dia das Mães, Black Friday).
2. Insira o termo em alta no **Motor Autônomo** ou no **SEO & Ubersuggest** do Nexus Bot.
3. A IA cruzará a tendência com o seu link de afiliado do Mercado Livre ou Shopee, gerando um Pin altamente direcionado para o que o mercado está a pesquisar ativamente naquele exato minuto.

---

## 3. Como configurar o webhook do ManyChat para integrar perfeitamente com os posts gerados?

A automação de DMs via ManyChat combinada com o Pinterest ou Instagram elimina o trabalho manual e dispara a conversão. Para integrar os links dinâmicos gerados pelo bot:

### Abordagem Prática (Sem necessidade de código complexo de Webhook):
Como o Nexus Bot gera um link de afiliado específico para cada produto minerado, a forma mais eficiente e estável de usar com o ManyChat é a **Automação por Palavra-Passe Dinâmica**:

1. **No Nexus Bot:** Quando o bot gera a copy, o CTA gerado é sempre padronizado (ex: *"Comenta **QUERO** que te envio o link exclusivo!"*).
2. **No ManyChat:**
   * Aceda a **Automation > New Automation**.
   * Defina o Trigger (Gatilho): **User Comments on Your Post/Reels**.
   * Defina a palavra-chave: `QUERO` (ou crie palavras-chave específicas por produto, ex: `ORGANIZADOR`).
   * Adicione o bloco de ação **Send Message**:
     > *"Olá! Que bom que demonstraste interesse. Aqui está o link direto com desconto no Mercado Livre para garantires o teu produto: [INSERIR_LINK_DE_AFILIADO]"*
3. **Fluxo de Trabalho Diário:** 
   * O bot gera o produto e a copy.
   * Você copia o link de afiliado gerado pelo Nexus e cola na resposta automática do ManyChat para aquele produto específico (ou usa um link de redirecionamento fixo na sua bio/ManyChat).
   * Quando o Pin no Pinterest ou o Reels for publicado e os utilizadores comentarem, o ManyChat entrega o link de forma imediata e invisível, gerando comissões no piloto automático.
