import streamlit as st
import nexus_copy as nxcopy 

def aplicar_id_afiliado(link, mkt):
    """Injeta seu ID 18316451024 para garantir a comissão"""
    if not link or link == "#":
        return link
    ID_FIXO_SHOPEE = "18316451024"
    link = str(link).strip()
    
    if mkt == "Shopee":
        # Remove lixo da URL e garante o parâmetro de rastreio
        base_link = link.split("?")[0]
        return f"{base_link}?smtt={ID_FIXO_SHOPEE}"
    return link

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão (AIDA & SEO)")
    
    # Recupera o nicho para o Gemini usar no SEO
    nicho_atual = st.session_state.get('foco_nicho', 'Ofertas')
    
    if st.session_state.get("sel_nome"):
        mkt = st.session_state.get('mkt_global', 'Shopee')
        
        # 1. Recupera e limpa o nome para a IA não se perder
        nome_bruto = st.session_state.sel_nome
        nome_limpo = nome_bruto.split('|')[0].replace("NOME:", "").replace("*", "").strip()
        
        # 2. Gera o link já com o seu CTA de afiliado
        link_final = aplicar_id_afiliado(st.session_state.sel_link, mkt)
        st.session_state.link_final_afiliado = link_final 

        with st.container(border=True):
            st.success(f"📦 **Produto Ativo:** {nome_limpo}")
            st.caption(f"🔗 Link Blindado: {link_final}")
        
        # 3. Disparo do Gemini (AIDA + SEO + CTA)
        if st.button("🔥 GERAR ESTRATÉGIAS VIRAIS (GEMINI)", use_container_width=True):
            with st.spinner("Gemini gerando copys de alta conversão..."):
                # O prompt do nxcopy já deve estar configurado para AIDA
                prompt = nxcopy.gerar_prompt_aida(nome_limpo, estilo="agressivo")
                prompt += f"\n\nContexto SEO/Nicho: {nicho_atual}."
                prompt += "\nInstrução Crítica: Inclua uma CTA (Chamada para Ação) poderosa. Separe 3 opções por ###."
                
                try:
                    # Usa o motor_ia_gemini (st.session_state.motor_ia_obj)
                    response = motor_ia_gemini.generate_content(prompt)
                    resultado = nxcopy.limpar_copy(response.text)
                    
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c) > 15]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no Gemini: {e}")

        # 4. Exibição das Munições Prontas
        if "res_arsenal" in st.session_state:
            for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
                with st.container(border=True):
                    st.markdown(f"#### 💎 Estratégia V{i+1}")
                    st.write(texto_copy)
                    
                    if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_{i}", use_container_width=True):
                        # Conecta o texto, a CTA e o link final com seu ID
                        micao_final = f"{texto_copy}\n\n🛒 LINK NO DIRECT: {link_final}"
                        st.session_state.copy_ativa = micao_final
                        st.toast("Enviado para o Estúdio!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
