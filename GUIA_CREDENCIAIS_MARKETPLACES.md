# Credenciais oficiais dos marketplaces

## Regra principal

O Nexus não deve receber cookies copiados do navegador, cabeçalhos de sessão ou tokens colados no chat. Cookies expiram, podem dar acesso à conta e podem violar os termos do marketplace. Eles também não são uma solução estável para CAPTCHA.

Use uma integração oficial quando existir. Quando não existir ou não estiver aprovada, use a busca manual, o link oficial do produto e o upload da imagem real.

## Mercado Livre

1. Crie ou selecione uma aplicação no [portal de desenvolvedores do Mercado Livre](https://developers.mercadolivre.com.br/).
2. Consulte o fluxo oficial de [OAuth e tokens](https://developers.mercadolivre.com.br/en_us/ruby/identity-and-access-management-oauth-and-tokens).
3. Configure no ambiente do Nexus, nunca no código:

```toml
ML_ACCESS_TOKEN = "APP_USR-..."
# ML_API_ACCESS_TOKEN = "..."  # alias aceito pelo Nexus
```

O token precisa ser de uma aplicação autorizada e pode precisar ser renovado. Um token não transforma a API em fonte de afiliado: o link de publicação continua sendo associado manualmente pelo portal de afiliados.

## Shopee

- Programa de afiliados: [affiliate.shopee.com.br](https://affiliate.shopee.com.br/)
- Open Platform: [open.shopee.com](https://open.shopee.com/)
- Guia de autorização: [Authorization and Authentication](https://open.shopee.com/developer-guide/20)

A Open Platform é voltada a integrações autorizadas e, em vários casos, exige conta de vendedor, Partner ID, Partner Key e autorização da loja. Não existe um cookie genérico recomendado para “liberar” a pesquisa pública.

## Amazon

- Associados Brasil: [Amazon Associados](https://associados.amazon.com.br/)
- Credenciais de publicidade: [Product Advertising API credentials](https://affiliate-program.amazon.com/assoc_credentials/home)
- Documentação atual: [Creators API / Amazon Advertising APIs](https://affiliate-program.amazon.com/help/node/topic/GBRCD467W33NMWLD)

A antiga PA-API está em transição para a Creators API. Use o portal que estiver disponível para a conta e região do associado. A SP-API é para vendedores, não substitui automaticamente a API de publicidade de afiliados.

## Configuração prática no Nexus

O Nexus aceita estes campos no ambiente/Secrets:

```toml
ML_ACCESS_TOKEN = "..."
ML_API_ACCESS_TOKEN = "..."
SHOPEE_TRACKING_ID = "..."
AMAZON_TRACKING_ID = "..."
```

Os IDs de rastreamento geram links de afiliado; não são tokens de pesquisa de catálogo.

## Quando o CAPTCHA continuar

1. Não repita muitas requisições nem tente contornar o CAPTCHA.
2. Use a API oficial aprovada ou selecione **Colar link oficial**.
3. Informe a URL do anúncio e faça upload da imagem real.
4. O Nexus bloqueará a campanha se não houver produto, link e imagem associados ao mesmo anúncio.

Essa política evita produto genérico, preço inventado, imagem de outro anúncio e link de busca apresentado como oferta.
