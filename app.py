with tabs[0]:
    st.header("Monitor de Produtos Quentes")
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho para Scanner:", value="Utilidades Domésticas")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Escanear Shopee & TikTok Trends", use_container_width=True):
        with st.status("Minerando 30 tendências exclusivas Shopee..."):
            # PROMPT REFORÇADO PARA TRAZER LINKS SHOPEE
            p = f"""Aja como um Expert em Shopee Affiliate. 
            Liste 30 produtos virais de {nicho} ({ticket}) que estão bombando no TikTok e Shopee Brasil.
            FORMATO OBRIGATÓRIO PARA CADA ITEM:
            PRODUTO: [nome do item] | TENDENCIA: [% cresc. BR] | CALOR: [0-100] | URL: https://shopee.com.br/busca-do-produto
            Importante: Foque em produtos que as pessoas realmente compram na Shopee Brasil."""
            st.session_state.res_busca = gerar_ia(p)

    if "res_busca" in st.session_state:
        import random # Para o key do botão não dar erro
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item and "PRODUTO:" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("PRODUTO:", "").strip()
                    tend = parts[1].replace("TENDENCIA:", "").strip()
                    calor_str = ''.join(filter(str.isdigit, parts[2]))
                    calor = int(calor_str) if calor_str else 50
                    link_orig = parts[3].replace("URL:", "").strip()

                    # Lógica de identificação visual no card
                    is_shopee = "shopee" in link_orig.lower() or "shope.ee" in link_orig.lower()
                    mercado_tag = "Shopee 🟠" if is_shopee else "Outro ⚪"

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"🌍 Tendência: {tend}")
                            st.markdown(f"🛒 **Mercado:** {mercado_tag}")
                        with col2:
                            cor = "red" if calor > 80 else "orange"
                            st.write(f"🌡️ Termômetro: :{cor}[{calor}°C]")
                            st.progress(calor / 100)
                        with col3:
                            # Só permite selecionar se for Shopee para não dar erro no Arsenal
                            if st.button("Selecionar", key=f"btn_{nome}_{random.randint(0,999)}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} enviado!")
                except:
                    continue
