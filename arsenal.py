def aplicar_id_afiliado(link, mkt):
    """Reconstrói o link garantindo o domínio e o ID 18316451024"""
    if not link or link == "#":
        return link
    
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Caso 1: Link de busca (Search)
        if "search?keyword=" in link:
            try:
                keyword = link.split("keyword=")[1].split("&")[0]
                return f"https://shopee.com.br/search?keyword={keyword}&smtt={ID_FIXO_SHOPEE}"
            except:
                return f"https://shopee.com.br/search?keyword=oferta&smtt={ID_FIXO_SHOPEE}"
        
        # Caso 2: Link de Produto Direto (Como esse das formas)
        # Pegamos apenas a parte principal do link antes de qualquer interrogação
        base_link = link.split("?")[0]
        
        # Se por algum erro o link vier sem o domínio, nós forçamos ele
        if "shopee.com.br" not in base_link:
            # Tenta pegar apenas o final (nome-do-produto-i.xxx.xxx)
            final_url = base_link.split("/")[-1]
            return f"https://shopee.com.br/{final_url}?smtt={ID_FIXO_SHOPEE}"
            
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    
    return link
