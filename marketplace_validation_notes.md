# Validação do Mercado Livre — 2026-08-18

A chamada direta `GET https://api.mercadolibre.com/sites/MLB/search` devolveu HTTP 403 com o corpo `{"message":"forbidden","error":"forbidden","status":403,"cause":[]}` neste ambiente, mesmo com User-Agent de navegador. A listagem pública `https://lista.mercadolivre.com.br/powerbank` também redirecionou no navegador para verificação/conta, embora a extração web tenha conseguido ler parcialmente a página e apresentado 4.231 resultados.

A página de produto individual extraída exigiu sessão e não expôs a imagem no ambiente anónimo. Portanto, a mineração ao vivo não pôde ser validada aqui por causa do bloqueio de acesso, e o código deve reportar essa condição honestamente, sem trocar o produto por uma imagem genérica.

A estratégia implementada no Nexus usa a API pública quando acessível e preserva `product_source_url`, `image_url`, `image_verified`, `image_source` e `product_external_id`. Em caso de bloqueio, o ciclo falha de forma explícita e exige uma URL oficial/thumbnail pública ou um token de acesso configurado, em vez de fabricar um anúncio ou reutilizar outro produto.

## Validação visual do dry run

A `source_product_image.jpg` e a `creative_image_a.jpg` foram abertas após o teste. A origem permaneceu separada, com 800×800 px; a Imagem A foi gerada em 1000×1500 px e exibiu o título `Power Bank 10000mah Carregador Portátil` e a CTA `VER OFERTA OFICIAL`. O fixture de teste usou uma imagem monocromática para isolar a passagem de dados; portanto, esta inspeção valida o encadeamento e não a aparência do anúncio real.
