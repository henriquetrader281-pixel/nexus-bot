# Máquina de Vídeos Nexus — arquitetura inicial

## Estado atual encontrado

O repositório é uma aplicação Python/Streamlit com pipeline local de mídia. A entrada principal está em `app.py` e `nexus_pipeline_ui.py`. O estado compartilhado é centralizado em `campaign_state.py`, que mantém compatibilidade com as chaves legadas do Streamlit. A geração atual reutiliza `media_pipeline.py` e `generate_creatives.py`, criando uma imagem vertical e um vídeo vertical curto com MoviePy/Pillow. O limite atual do vídeo gerado é de três cenas de aproximadamente 3,3 segundos, totalizando cerca de 10 segundos.

O projeto já possui armazenamento SQLite em `metrics_store.py`/`metrics_schema.sql` com campanhas, criativos, publicações e métricas agregadas por variante e canal. A memória atual em `self_optimizer.py` escolhe variantes com base em evidências mínimas de impressões e cliques. A narração possui fallback para gTTS em `tts_engine.py`.

## Arquitetura escolhida para o MVP

A primeira entrega será incremental sobre o app Streamlit existente, sem migrar a base para outro framework. Isso preserva os testes e o pipeline local já funcional e permite incorporar edição por cenas sem duplicar a lógica de campanha, mídia ou métricas.

A nova camada terá quatro responsabilidades:

1. **Agentes especializados**: roteirista, estrategista de retenção, diretor visual, editor de cenas, voz/legendas e analista de métricas. Cada agente terá um contrato explícito, um provedor configurável e fallback determinístico quando não houver chave de API.
2. **Projeto de vídeo**: manifesto JSON versionado contendo formato, cenas, textos, duração, mídia, áudio, legendas, thumbnail, parâmetros de renderização e histórico de ajustes. O projeto será salvo dentro de `.nexus_media` e referenciado pelo estado compartilhado.
3. **Renderização local**: reaproveitar Pillow/MoviePy e limitar a duração padrão a 15 minutos, com presets verticais 9:16 para TikTok/Shorts e parâmetros editáveis por cena. A publicação automática não será ativada.
4. **Memória e métricas**: ampliar o SQLite com projetos, agentes, versões, experimentos e recomendações, mantendo compatibilidade com `creative_performance` e com o otimizador baseado em evidências reais.

## Integrações e custo

O núcleo deverá funcionar sem serviços pagos: regras locais, templates, gTTS e renderização local. APIs externas serão opcionais por variável de ambiente. Quando a integração de rede social não estiver configurada, a interface oferece exportação e importação manual de métricas. Nenhuma rotina deve publicar automaticamente sem confirmação explícita.

## Opções de execução

| Abordagem | Tradeoffs | Custo | Complexidade de configuração |
|---|---|---:|---:|
| Evoluir o app Streamlit atual e executar localmente ou em um servidor Python já disponível | Melhor compatibilidade com MoviePy/Pillow e os testes atuais; precisa deixar o processo disponível para renderizações e métricas agendadas | Sem custo de serviço no núcleo; depende da máquina do usuário | Baixa a média |
| Migrar para uma aplicação web gerenciada com backend e jobs | Acesso mais simples pelo navegador e melhor base para colaboração; renderização com dependências nativas e armazenamento de vídeos exige adaptações e pode ter limites de execução | Gratuito para começar, sujeito a limites do provedor e às APIs de IA | Média a alta |

Para respeitar o pedido de começar gratuitamente e reduzir risco, a implementação inicial seguirá a primeira abordagem, mantendo contratos de integração que permitam uma migração posterior.

## Fora do MVP inicial

Não será implementado disparo automático para TikTok ou YouTube, nem promessa de crescimento garantido. As diretrizes de cada canal serão tratadas como validações de formato, direitos autorais, transparência e revisão humana; métricas reais serão importadas ou conectadas somente quando o usuário configurar as credenciais adequadas.
