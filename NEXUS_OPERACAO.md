# Nexus Bot — operação consolidada

O Nexus reúne mineração, análise de tendências, copy, palavras-chave, narração, geração de imagem, vídeo, fila de campanhas, métricas e modo autônomo. Para reduzir a confusão causada pela quantidade de recursos, o fluxo recomendado começa sempre pela **Esteira Principal**.

## Inicialização

Use `./run.sh` para iniciar o painel visual. O script cria ou reutiliza o ambiente virtual, instala as dependências e inicia o Streamlit:

```bash
export NEXUS_PASSWORD='uma-senha-forte'
./run.sh
```

O modo autônomo legado continua disponível sem remover a funcionalidade existente:

```bash
export NEXUS_MODE=autonomous
./run.sh
```

## Ordem recomendada da operação

| Ordem | Área | O que fazer | Saída |
|---:|---|---|---|
| 1 | Diagnóstico | Abra **Avançado → Diagnóstico de operação** e corrija os itens obrigatórios. | Confirmação de dependências, FFmpeg e credenciais. |
| 2 | Mineração | Busque tendências ou produtos e selecione um anúncio com imagem pública. | Produto, marketplace, tendência e imagem-fonte. |
| 3 | Análise | Confirme a dor, palavras-chave e hooks. | Intenção de compra, keywords, hooks e CTAs. |
| 4 | Produção | Clique em **Gerar pacote completo**. | Copy AIDA, legenda, áudio, Imagem A e Vídeo B. |
| 5 | Revisão | Confira texto, imagem, vídeo, áudio e manifesto. | Pacote `ready` ou `needs_review`. |
| 6 | Afiliado | Associe o link oficial do portal. | Campanha pronta para publicação manual. |
| 7 | Métricas | Registre impressões, cliques e conversões. | Base para auto-otimização baseada em evidência. |

## Diagnóstico de falhas

Se a mineração falhar, use uma busca manual, uma URL de produto ou um upload real de imagem. Se a copy com IA falhar, o fallback local gera texto estruturado. Se a ElevenLabs estiver indisponível, o gTTS pode gerar uma narração básica. Se o áudio não existir, o Vídeo B continua podendo ser criado com texto na tela.

O diagnóstico não exibe valores de chaves. Ele apenas informa se uma credencial está presente. As chaves devem permanecer em `.streamlit/secrets.toml` ou em variáveis de ambiente.

## Eficiência

O áudio é identificado por hash do roteiro e a mídia por uma impressão digital dos insumos. Repetir uma campanha sem alterar imagem, produto, hooks ou áudio reutiliza os arquivos já existentes. O manifesto registra copy, keywords, hooks, legenda, origem da imagem, hash da fonte, áudio e status de publicação.

## Escopo de publicação

A publicação automática permanece desligada por segurança. O sistema prepara e organiza os ativos, mas a decisão final de revisar, associar o link e publicar continua manual.
