import streamlit as st
import nexus_copy as nxcopy  # 🔱 Mudamos aqui para evitar conflito com a biblioteca padrão do Python

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com seu ID Shopee 18316451024"""
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Limpa lixo de URL e injeta o smtt
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # --- JUNÇÃO ELITE: RECUPERA O NICHO DO SCANNER ---
    # Isso evita o erro "name 'nicho' is not defined"
    nicho_atual = st.session_state.get('foco_nicho', 'Ofertas Imperdíveis')
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.mkt_global
        bruto = st.session_state.sel_nome
        
        # 🛡️ Limpeza: Pega apenas o nome real para a IA focar na venda
        nome_limpo = bruto.split('|')[0].replace("NOME:", "").strip()
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        
        with st.container(border=True):
            st.success(f"📦 **Produto Selecionado:** {nome_limpo}")
            st.markdown("#### 🔗 Link Rastreando Comissão")
            st.code(link_final, language="text")

        st.divider()

        # Botão padrão 2026
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (AIDA)", use_container_width=True):
            with st.spinner("Conectando ao Cérebro de Marketing Gemini Plus..."):
                
                # 🧠 Chamando a função do arquivo nexus_copy.py 
                # Adicionamos o nicho_atual para a IA saber o contexto exato
                prompt_mestre = nxcopy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                prompt_mestre += f" Considere que o nicho é {nicho_atual}."
                
                try:
                    # Dispara para o motor (já blindado contra erro de hash usando o motor_ia do app.py)
                    resultado_bruto = miny.minerar_produtos(prompt_mestre, mkt, motor_ia)
                    
                    # 🧼 Limpa saudações da IA usando o nexus_copy
                    resultado = nxcopy.limpar_copy(resultado_bruto)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                except Exception as e:
                    # Se der erro de hash, o usuário já sabe como ajustar no mineracao.py (adicionando _)
                    st.error(f"Erro no disparo do Arsenal: {e}")

        # Exibição dos Cards de Munição
        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:5]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia de Elite V{i+1}")
                    st.write(texto_copy)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", use_container_width=True):
                        # --- CONEXÃO TOTAL NEXUS ---
                        micao_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.session_state.copy_ativa = micao_final # Envia para Estúdio
                        st.session_state.copy_final_pronta = micao_final # Envia para Postador
                        st.session_state.link_final_afiliado = link_final # Para o Postador usar no ManyChat
                        st.session_state.sel_link_blindado = link_final # Backup
                        # -----------------------------------------------
                        st.toast(f"Munição V{i+1} enviada ao Estúdio e Postador!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
