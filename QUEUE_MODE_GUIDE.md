# Modo Nexus: minerar e preparar, publicar manualmente

## Objetivo

O ciclo automático não publica em Pinterest, Instagram, TikTok, ManyChat ou Make. Ele pesquisa produtos, valida a imagem do mesmo anúncio, cria copy, hooks, palavras-chave, legenda, áudio, Imagem A e Vídeo B e guarda o pacote na fila `prepared_campaigns`.

## Esteira

1. O minerador procura o produto no Mercado Livre usando a API e o fallback web quando possível.
2. A campanha recebe título, origem do anúncio, imagem-fonte e evidências de imagem.
3. O motor editorial cria copy AIDA, hooks, intenção, palavras-chave, CTA e legenda.
4. A voz é gerada pelo ElevenLabs ou fallback configurado.
5. A pipeline cria `creative_image_a.jpg` em 1000×1500 e `creative_video_b.mp4` em 1080×1920.
6. O conjunto é salvo em `prepared_campaigns` com status `ready`.
7. A Central de Disparo lista os pacotes prontos. O utilizador carrega um pacote, revisa a prévia, cola o link oficial do Portal de Afiliados e publica manualmente.

## Campos manuais

O link não é fabricado pelo Nexus. Na Central de Disparo, cole o URL oficial recebido no Portal de Afiliados e selecione **Associar link à campanha**. Só depois disso a publicação manual do Pinterest fica habilitada. Instagram e TikTok continuam exigindo um URL HTTPS público do Vídeo B.

## Execução automática

O worker headless deve chamar:

```python
executar_ciclo_mestre_um_clique(provedor="gemini", publicar=False)
```

O argumento `publicar=False` permanece explícito para evitar regressões. Mesmo chamadas antigas com `publicar=True` são tratadas pela política atual como preparação manual.

## Persistência

O SQLite procura primeiro um caminho configurado em `NEXUS_METRICS_DB`, depois `.nexus_media/nexus_metrics.sqlite3` e, por último, `/tmp/nexus_metrics.sqlite3`. Os arquivos de imagem, vídeo e áudio são guardados no diretório de mídia da campanha. Para manter os arquivos entre reinícios de uma infraestrutura efêmera, deve ser adicionado um storage externo; sem isso, a fila pode manter o registo, mas os caminhos locais podem deixar de existir após o ambiente ser recriado.

## Credenciais mínimas

A mineração autónoma do Mercado Livre pode exigir `ML_ACCESS_TOKEN` ou `ML_API_ACCESS_TOKEN` quando o endpoint público responder 403. A publicação manual exige apenas as credenciais da rede escolhida no momento do disparo. O ciclo de preparação não precisa de `PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID` ou `MANYCHAT_WEBHOOK_URL`.
