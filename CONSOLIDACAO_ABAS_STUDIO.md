# Consolidação das abas e correção do Estúdio Nexus

## Diagnóstico

A aplicação tinha várias fontes de estado independentes. O Scanner, Trends, Radar e Espionagem Global gravavam apenas parte do produto; o Arsenal guardava uma copy separada; o Estúdio criava prompts e links de pesquisa; e a Central de Disparo procurava chaves legadas. Por isso, era possível encontrar uma luminária, selecionar um organizador e abrir um Estúdio sem campanha ou com imagem incompatível.

## Estrutura consolidada

| Setor novo | Funcionalidades reunidas | Fonte de verdade |
|---|---|---|
| **Inteligência & Leads** | Sniper de Leads e Espionagem Global | `nexus_campaign` |
| **Descoberta** | Scanner, Google Trends e Radar | `nexus_campaign` |
| **Studio & Copy** | Arsenal AIDA, Imagem A, Vídeo B, voz e prompt opcional | `nexus_campaign` |
| **Central de Disparo** | Prévia, Pinterest, Instagram e TikTok | `nexus_campaign` |
| **Afiliados** | ID, vitrine e colagem do link oficial | `nexus_campaign` |

O módulo `campaign_state.py` mantém compatibilidade com as chaves antigas, mas todas as novas alterações passam pelo dicionário central `nexus_campaign`. Ao trocar de produto, o sistema elimina automaticamente link, copy, imagem, vídeo, leads e SEO herdados da campanha anterior.

## Correção da mídia

O botão do Estúdio deixou de apenas preparar um prompt para o Google Labs. Ao clicar em **GERAR IMAGEM A + VÍDEO B**, o Nexus resolve o link oficial, extrai a imagem pública do produto, cria uma composição vertical 1000×1500, monta um Vídeo B H.264 vertical 1080×1920 com três cenas e grava um manifesto da campanha. A voz ElevenLabs ou gTTS pode ser anexada antes da renderização.

> O pipeline local é uma composição comercial determinística baseada na imagem real do produto. Ele não inventa uma nova fotografia 3D do produto. Isso reduz o risco de trocar o produto por outro objeto e mantém marca, forma e detalhes da referência.

O link oficial do Portal do Afiliado é preservado. O sistema não recria `matt_word`, `matt_tool`, `ref` nem outros parâmetros dos links `meli.la`.

## Validação executada

| Teste | Resultado |
|---|---|
| Compilação dos módulos consolidados | Aprovado |
| Troca de produto sem herdar ativos antigos | `CAMPAIGN_STATE_TEST_OK` |
| Resolução de link, imagem, Imagem A e Vídeo B | `CAMPAIGN_MEDIA_PIPELINE_TEST_OK` |
| Inicialização do Streamlit e navegação consolidada | `APP_STRUCTURE_TEST_OK` |
| Vídeo de teste | H.264, 1080×1920, aproximadamente 9,875 s |

## Limitações que continuam intencionais

O Pinterest só pode publicar quando `PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID`, um link oficial e uma imagem pública estiverem disponíveis. Instagram e TikTok exigem um URL HTTPS público do Vídeo B; um caminho local no servidor não é suficiente. Sem o link oficial de um produto, Trends, Radar e Espionagem Global alimentam a oportunidade, mas não podem fingir que existe uma oferta validada.

## Publicação

As alterações foram enviadas para o branch `main` do repositório [henriquetrader281-pixel/nexus-bot](https://github.com/henriquetrader281-pixel/nexus-bot). Commits principais: `37b2c90` para a consolidação e `501dbf7` para a sincronização do fallback de Trends.
