def aplicar_id_afiliado(link, mkt):
    """Reconstrói o link do zero para evitar erros de 'link cortado'"""
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # 1. Se for link de busca (search)
        if "search?keyword=" in link:
            try:
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=produto&smtt={ID_FIXO_SHOPEE}"
        
        # 2. Se for link de produto direto (como o da Forma de Bolo)
        # Extraímos a parte do nome do produto e os códigos de ID (i.123.456)
        if "/product/" in link or "-i." in link:
            # Removemos tudo após a interrogação de rastreio original
            base_produto = link.split("?")[0]
            # Garantimos que o link comece com o domínio correto
            if not base_produto.startswith("http"):
                base_produto = "https://shopee.com.br" + base_produto
            
            return f"{base_produto}?smtt={ID_FIXO_SHOPEE}"
            
    return link
