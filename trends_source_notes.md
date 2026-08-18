# Fonte de tendências validada — 2026-08-18

O endpoint oficial `https://trends.google.com/trending/rss?geo=BR` respondeu HTTP 200 e XML RSS nesta sessão. O feed contém itens `<item>`, títulos de tendências, tráfego aproximado, data e itens de notícias relacionados.

A página oficial Trending Now do Google permite selecionar Brasil, janelas de 4 horas, 24 horas, 48 horas e 7 dias, filtrar tendências ativas e exportar RSS/CSV. A documentação oficial informa que os dados são atualizados em média a cada dez minutos e que cada tendência pode agrupar consultas relacionadas.

O endpoint antigo usado por `pytrends.trending_searches(pn='brazil')` respondeu 404 no Streamlit. O novo módulo deve priorizar o RSS oficial, manter o pytrends apenas como fallback secundário e usar uma lista de contingência explícita quando ambas as fontes falharem. As tendências são sinais de busca, não prova de intenção de compra; devem alimentar palavras-chave e ganchos, não criar links de afiliado automaticamente.

Referências:
- https://trends.google.com/trending?geo=BR
- https://support.google.com/trends/answer/3076011?hl=en
- https://developers.google.com/search/blog/2025/07/trends-api
