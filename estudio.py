if st.button("🔥 GERAR NOVA MUNIÇÃO AIDA + LINK", use_container_width=True):
            with st.spinner("Forçando IA a agir como Especialista em Reels..."):
                
                # PROMPT DE COPYWRITER NÍVEL TIKTOK (Mais agressivo e sem links soltos)
                prompt_aida = f"""IGNORE TODAS AS INSTRUÇÕES ANTERIORES. Atue como um Criador de Conteúdo Viral para Reels/TikTok.
Escreva UMA ÚNICA legenda curta e explosiva para o produto: '{produto_foco}'.
REGRA 1: NUNCA use saudações como 'Atenção fulano'. Comece direto com o problema/dor (Ex: 'Você ainda passa raiva com...').
REGRA 2: Seja muito informal, use emojis.
REGRA 3: É ESTRITAMENTE PROIBIDO colocar links, URLs ou sites no meio do seu texto. O sistema fará isso depois.
REGRA 4: O CTA final deve ser APENAS: 'Comenta EU QUERO que te mando o link no Direct!'."""
                
                try:
                    resultado = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # FILTRO DE LIMPEZA FÍSICA
                    linhas_limpas = []
                    for linha in resultado.split('\n'):
                        if "NOME:" not in linha and "CALOR:" not in linha and "http" not in linha:
                            linhas_limpas.append(linha)
                    
                    texto_final_ia = "\n".join(linhas_limpas).strip()
                    
                    # 🔗 BLINDAGEM DO LINK CORRIGIDA (À prova de falhas)
                    link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
                    
                    # Se o link tiver parâmetros (?), a gente corta e limpa. Se não, só usa a base.
                    if "http" in link_raw:
                        link_base = link_raw.split('?')[0]
                    else:
                        link_base = "https://shopee.com.br"
                        
                    # Adiciona o seu ID da Shopee de forma limpa
                    link_final = f"{link_base}?smtt=18316451024"

                    # Monta o texto final com o link isolado no fundo
                    st.session_state.copy_final_pronta = f"{texto_final_ia}\n\n🛒 **SEU LINK DE AFILIADO:** {link_final}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Aguarde o reset da IA: {str(e)}")

        if "copy_final_pronta" in st.session_state:
            st.text_area("Sua munição (Legenda Viral + Link Shopee):", value=st.session_state.copy_final_pronta, height=200)
