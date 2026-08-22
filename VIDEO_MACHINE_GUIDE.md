# Máquina de Vídeos Nexus

A Máquina de Vídeos foi integrada ao aplicativo Streamlit existente do Nexus. Ela funciona como um estúdio vertical com projetos versionados, agentes especializados, edição por cenas, renderização local, legendas VTT, thumbnail e memória de decisões. O núcleo funciona em **modo local**, sem chaves de IA e sem custo por chamada; provedores compatíveis com Chat Completions podem ser ativados opcionalmente por variáveis de ambiente.

> O sistema é uma ferramenta de produção e teste. Ele não garante viralização, views, aprovação de monetização ou lucro. O aprendizado usa apenas métricas reais informadas pelo usuário ou por integrações futuras.

## O que foi adicionado

| Área | Entrega |
|---|---|
| Navegação | Aba `🎬 MÁQUINA DE VÍDEOS` e aba `📈 MÉTRICAS` no `app.py`. |
| Agentes | Estrategista, roteirista, diretor visual, editor de ritmo, voz/legendas, diretor de capa, analista e revisor de conformidade. |
| Editor | Projeto versionado com cenas, duração, texto, legenda, prompt visual, transição e estado ativo/inativo. |
| Render | MP4 vertical, frames por cena, thumbnail JPG e legendas VTT usando Pillow e MoviePy. |
| Memória | Histórico local de execuções e aprendizados em `.nexus_media/video_memory.json`, limitado e auditável. |
| Métricas | SQLite para publicações e leituras por TikTok, YouTube e Instagram, incluindo views, impressões, retenção, conclusão, curtidas, comentários, compartilhamentos, cliques e variação de seguidores. |
| Segurança operacional | Exportação manual, revisão humana obrigatória, bloqueio de cenas vazias e limite de duração por canal. |

## Como executar

Na raiz do repositório:

```bash
chmod +x run.sh
./run.sh
```

O `run.sh` cria o ambiente virtual, instala o `requirements.txt` e inicia o executor existente do Nexus. Para abrir diretamente a interface web durante o desenvolvimento, use:

```bash
streamlit run app.py
```

A senha padrão do aplicativo continua sendo a já existente no projeto. Em produção, defina `NEXUS_PASSWORD` por variável de ambiente ou secret e não use a senha padrão.

## Fluxo recomendado

Primeiro abra `🎬 MÁQUINA DE VÍDEOS`, informe o produto ou tema, nicho e canal, e crie o projeto. Depois, suba uma imagem real do produto se houver uma. A URL pública da imagem já presente na campanha é passada aos agentes visuais quando o provedor remoto estiver ativado.

Execute **Executar equipe de IA**. Em modo local, o sistema gera um plano determinístico e editável. Em modo remoto, cada agente usa seu modelo configurado individualmente. Revise a linha do tempo, altere textos, legendas, duração e prompts, e só então execute **Renderizar MP4**. A exportação produz o vídeo, a capa e o arquivo VTT; nenhum canal social é acionado.

Após publicar manualmente, abra `📈 MÉTRICAS`, registre a publicação e informe os números reais do painel do canal. O botão **Analisar e registrar aprendizado** cria hipóteses de teste na memória do projeto. O próximo ciclo pode usar esses aprendizados, mas o sistema não muda a estratégia por amostra pequena como se fosse uma conclusão estatística.

## Provedores de IA

O padrão é local:

```toml
NEXUS_AI_PROVIDER = "local"
```

Para usar um endpoint compatível com Chat Completions, configure os secrets no ambiente, nunca no Git:

```toml
NEXUS_AI_PROVIDER = "openai-compatible"
NEXUS_OPENAI_API_KEY = "sua-chave"
NEXUS_OPENAI_BASE_URL = "https://seu-endpoint/v1"
NEXUS_AGENT_ROTEIRO_MODEL = "gpt-5-mini"
NEXUS_AGENT_DIRECAO_VISUAL_MODEL = "gemini-3-flash-preview"
NEXUS_AGENT_ANALISTA_MODEL = "gpt-5-mini"
```

Cada agente possui modelo padrão, mas todos podem ser substituídos com `NEXUS_AGENT_<AGENTE>_MODEL`. Se uma chamada falhar, a interface registra o erro e usa o fallback local. O uso de qualquer serviço remoto depende da disponibilidade, dos limites e dos termos do respectivo provedor; portanto, “gratuito” não significa ilimitado.

## Compatibilidade de canais e conformidade

O projeto usa o formato vertical 9:16 e mantém o teto interno de 15 minutos. Para YouTube Shorts, o editor reduz o limite para 180 segundos porque a página oficial de upload informa que Shorts enviados pelo computador podem ter até 3 minutos e proporção quadrada ou vertical [1]. O TikTok informa que vídeos enviados podem ter até 60 minutos, mas o produto aplica um limite mais conservador de 15 minutos para manter o foco em vídeos curtos e facilitar a revisão [2].

A escolha do que testar deve considerar retenção, conclusão, engajamento e correspondência entre tema e público, não apenas views. O próprio TikTok descreve sinais de interação, informações do conteúdo e informações do usuário como fatores de recomendação, indicando que assistir até o fim, pular, curtir, comentar e compartilhar são sinais observáveis, mas não uma promessa de distribuição [3].

Quando o conteúdo for gerado ou significativamente alterado por IA, revise os rótulos e divulgações exigidos pela plataforma. O TikTok orienta a identificação de conteúdo realista gerado ou alterado por IA para dar contexto ao público [4]. O sistema inclui aviso de conteúdo promocional e mantém a publicação manual para que o usuário possa revisar direitos autorais, alegações, publicidade e configurações da conta antes do envio.

## Estrutura principal

| Arquivo | Responsabilidade |
|---|---|
| `video_machine/agents.py` | Contratos de agentes, provedor local, provedor remoto opcional e fallback. |
| `video_machine/project_store.py` | Projetos, cenas, versões, presets e persistência JSON. |
| `video_machine/render_engine.py` | Composição de cenas, MP4, thumbnail e VTT. |
| `video_machine/studio_tab.py` | Interface do estúdio e edição da linha do tempo. |
| `video_machine/metrics_tab.py` | Registro e visualização de métricas por canal. |
| `video_machine/memory_store.py` | Memória local de execuções, preferências e aprendizados. |
| `video_machine/validation.py` | Validações antes do render. |
| `metrics_store.py` | Persistência SQLite legada e nova camada de métricas de vídeo. |
| `metrics_schema.sql` | Schema de campanhas, publicações, projetos e métricas. |

## Limites conhecidos do MVP

O editor atual é baseado em cenas e controles Streamlit, não em uma timeline drag-and-drop com preview em tempo real como um editor comercial. Os agentes visuais produzem prompts e verificações; a geração semântica de novas imagens depende de uma integração externa configurada, enquanto o renderizador local usa a imagem-fonte e layouts determinísticos. Não há publicação automática nem coleta automática de TikTok/YouTube nesta primeira entrega, porque isso exige credenciais, permissões e contratos de API que devem ser configurados separadamente.

## Testes executados

Os testes de núcleo, render, métricas e estrutura do app são executados com:

```bash
python3 -m pytest -q test_video_machine.py test_video_render_smoke.py test_video_metrics.py test_video_validation.py test_metrics_store.py test_app_structure.py
```

A validação inclui a geração real de um MP4 curto, thumbnail e legendas VTT em diretório temporário.

## Referências

[1]: https://support.google.com/youtube/answer/12779649?hl=en&co=GENIE.Platform%3DDesktop "YouTube Help — Upload YouTube Shorts"

[2]: https://support.tiktok.com/en/using-tiktok/creating-videos/camera-tools "TikTok Help Center — Camera tools"

[3]: https://support.tiktok.com/en/using-tiktok/exploring-videos/how-tiktok-recommends-content "TikTok Help Center — How TikTok recommends content"

[4]: https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content "TikTok Newsroom — New labels for disclosing AI-generated content"
