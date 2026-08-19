# Nexus Media Extractor

A extensão recuperada do Nexus é uma extensão Chromium Manifest V3 que analisa a página ativa quando o utilizador abre o popup. Ela localiza imagens, posters de vídeo, elementos `video` e `source`, imagens Open Graph, `srcset`, imagens de fundo CSS e URLs públicas de imagem/vídeo expostas no HTML.

## Instalação local

Abra `chrome://extensions`, ative o **Modo de programador**, selecione **Carregar sem compactação** e escolha esta pasta `Nexus_Extension`. A extensão não precisa de um servidor separado.

## Utilização

Depois de abrir uma página de produto, clique na extensão e selecione **Analisar página**. Os recursos encontrados aparecem com pré-visualização. É possível descarregar um item isolado pelo botão de download ou selecionar vários recursos e usar **Descarregar selecionados**. Os ficheiros são guardados na pasta `Nexus/` dentro do diretório de downloads do navegador.

A opção **Copiar para o Nexus** coloca no clipboard um objeto JSON com os campos já reconhecidos por `campaign_state.py`:

```json
{
  "product_name": "Título da página",
  "product_source_url": "https://exemplo.test/produto",
  "image_url": "https://cdn.exemplo.test/produto.jpg",
  "source_image_url": "https://cdn.exemplo.test/produto.jpg",
  "video_source_url": "https://cdn.exemplo.test/produto.mp4",
  "media": [
    {"type": "image", "url": "...", "source": "img[src]"}
  ],
  "source": "browser_extension",
  "extracted_at": "2026-08-19T00:00:00.000Z"
}
```

Na versão atual, a transferência para o Nexus é feita copiando esse JSON e colando-o no fluxo que receberá a campanha. O código mantém também a função de copiar um link com o parâmetro de afiliado configurável, preservando o comportamento da extensão original.

## Limitações

A extensão encontra URLs que o navegador expõe no DOM, em metadados, em estilos computados, no HTML e na Performance Resource Timeline da página. Para players dinâmicos, reproduza alguns segundos do vídeo antes de abrir o popup e clique novamente em **Analisar página**; isso permite que a extensão veja os recursos registados pelo navegador. Ela não ultrapassa autenticação, paywalls, CORS, DRM, URLs `blob:` ou recursos protegidos pelo próprio site. Um endereço `.m3u8` é identificado como recurso de vídeo, mas pode representar apenas uma playlist HLS; nesse caso, o download direto não produz necessariamente um ficheiro MP4.

A extensão não publica conteúdo, não cria novos links de afiliado automaticamente e não envia dados para um servidor externo. O botão de exportação apenas copia o JSON localmente para o clipboard.
