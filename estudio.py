import streamlit as st

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. SEGURANÇA
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Selecione um produto no Scanner antes de entrar no Estúdio!")
        return

    # 2. LIMPEZA DO NOME
    produto_foco = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # --- 🔗 INTEGRAÇÃO COM O ARSENAL ---
    if "copy_ativa" in st.session_state and st.session_state.copy_ativa != "":
        st.success("✅ Copy de Alta Conversão recebida do Arsenal!")
        
        link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
        link_base = link_raw.split('?')[0].split('|')[0].strip()
        link_final = f"{link_base}?smtt=18316451024"

        st.session_state.copy_final_pronta = f"{st.session_state.copy_ativa}\n\n🛒 **COMPRE AQUI:** {link_final}"
        st.session_state.copy_ativa = ""

    # --- CONTAINER DA LEGENDA ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia: **{produto_foco}**")
        
        if st.button("🔥 GERAR NOVA MUNIÇÃO AIDA + LINK", use_container_width=True):
            with st.spinner("Forçando IA a agir como Copywriter Sênior..."):
                
                # PROMPT BLINDADO (Hack Master)
                prompt_aida = f"""IGNORE INSTRUÇÕES DE MINERAÇÃO E BUSCA. NÃO LISTE PRODUTOS. Aja APENAS como um Copywriter de redes sociais.
Escreva UMA ÚNICA LEGENDA viral e persuasiva para o produto: '{produto_foco}'.
Use formato AIDA direto. Sem hashtags e sem introdução. Apenas o texto persuasivo focando na dor do cliente e chamando para a ação."""
                
                try:
                    resultado = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # FILTRO DE LIMPEZA FÍSICA (Destrói a lista se a IA teimar)
                    linhas_limpas = []
                    for linha in resultado.split('\n'):
                        if "NOME:" not in linha and "CALOR:" not in linha and "TICKET:" not in linha and "URL:" not in linha:
                            linhas_limpas.append(linha)
                    
                    texto_final_ia = "\n".join(linhas_limpas).strip()
                    
                    # Blindagem do Link
                    link_raw = st.session_state.get('sel_link', 'https://shopee.com.br')
                    link_base = link_raw.split('?')[0].split('|')[0].strip()
                    link_final = f"{link_base}?smtt=18316451024"

                    st.session_state.copy_final_pronta = f"{texto_final_ia}\n\n🛒 **COMPRE AQUI:** {link_final}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Aguarde o reset da IA: {str(e)}")

        if "copy_final_pronta" in st.session_state:
            st.text_area("Sua munição (Legenda Limpa + Link Shopee):", value=st.session_state.copy_final_pronta, height=200)

    st.divider()

    # --- CONTAINER DO ROTEIRO ---
    st.markdown("#### 🎥 Mapa de Cortes (Direção de Arte)")
    if st.button("🧠 GERAR ROTEIRO DE ALTA RETENÇÃO", use_container_width=True):
        with st.spinner("Criando mapa de cenas..."):
            prompt_video = f"""IGNORE BUSCA. Atue como Diretor de Marketing. Crie um roteiro de edição prático de 15s para o produto: {produto_foco}.
Divida a edição no formato AIDA visual:
[0-3s] HOOK VISUAL: Cena para prender a atenção.
[3-10s] DESEJO/DOR: Demonstração do produto.
[10-15s] CTA: Chamada final na tela."""
            try:
                res_roteiro = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
                
                # FILTRO PARA O ROTEIRO TAMBÉM
                linhas_rot = []
                for linha in res_roteiro.split('\n'):
                    if "NOME:" not in linha and "CALOR:" not in linha:
                        linhas_rot.append(linha)
                        
                st.session_state.roteiro_video = "\n".join(linhas_rot).strip()
                st.rerun()
            except:
                st.error("IA em resfriamento. Tente em instantes.")

    if "roteiro_video" in st.session_state:
        with st.expander("🎞️ ROTEIRO CAPCUT", expanded=True):
            st.markdown(st.session_state.roteiro_video)
