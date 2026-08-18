# Auditoria visual dos criativos

A primeira Imagem A foi gerada em 1000x1500, mas o título inicialmente foi cortado no meio de uma palavra. O gerador foi corrigido para quebrar linhas por palavras e limitar o título a cinco palavras.

O segundo teste confirmou que o gerador consegue resolver o link oficial `https://meli.la/11v5uxd`, preservar esse URL no manifesto, extrair a imagem Open Graph pública e produzir um vídeo H.264 em 1080x1920 com aproximadamente 9,875 segundos. A publicação não foi executada.

## Auditoria do pipeline integrado

O teste do novo contrato de campanha produziu uma Imagem A em 1000x1500 e um quadro do Vídeo B em 1080x1920 usando o mesmo power bank real, sem trocar para teclado ou luminária. A Imagem A contém CTA de oferta oficial; o quadro do vídeo mantém o mesmo produto e a mesma identidade visual. O Vídeo B é um slideshow vertical com cortes e texto gerado a partir do nome da campanha. O resultado é uma composição comercial determinística com a imagem real do produto, não uma geração fotorealística nova do objeto.
## Auditoria do Vídeo B anexado — 2026-08-18

Os quadros 01 e 02 mostram uma imagem de uma mini pistola de massagem, mas o texto sobreposto está duplicado e fora da área segura. Na primeira cena aparecem simultaneamente “Você ainda sofre com isso?”, “Missão? Pistola de Massagem Muscular”, “Pare o scroll: Mini Pistola de Massagem Muscular Elétrica” e “Praticidade para o dia a dia”, com linhas a colidir. Na segunda cena, o título “Mini Pistola de Massagem Muscular” também se repete e sobrepõe a sublegenda. A CTA “VER OFERTA OFICIAL” aparece como botão no fundo e como outra camada inferior, indicando que a fonte usada para a cena já contém texto ou que um criativo anterior foi reutilizado como imagem-fonte. A correção deve separar a imagem-fonte original dos criativos gerados, usar uma única headline e subheadline por cena, e desenhar uma única CTA dentro de um painel opaco.

## Validação visual do Vídeo B corrigido — 2026-08-18

Os quadros corrigidos usam a imagem-fonte sem texto herdado. Cada cena tem uma headline, uma subheadline e uma única CTA dentro de painel escuro. O primeiro quadro mostra o gancho “Você ainda fica sem bateria?” com “Power Bank 10000mah”; o segundo mostra “Power Bank 10000mah” e “Veja uma solução prática.” Não há sobreposição nem CTA duplicada. A referência visual continua coerente com o nome da campanha no teste; o fundo do teste foi uma imagem local simples, portanto a validação de identidade visual do produto real depende da imagem-fonte correta fornecida pelo marketplace ou pelo upload manual.
