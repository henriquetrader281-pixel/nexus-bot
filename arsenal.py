import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re

def aplicar_id_afiliado(link, mkt):
    """Garante o rastreio com ID Shopee 18316451024"""
    if not link or len(str(link)) < 10: return link
    ID_FIXO_SHOPEE = "18316451024"
    
    # Limpeza de lixo
    link_limpo = str(link).split("###")[0].split("\n")[0].strip()
    link_limpo = re.sub(r'[\*\t\r]', '', link_limpo).replace(" ", "")

    if mkt == "Shopee":
        try:
            base = link_limpo.split("?")[0].split("#")[0].rstrip("/")
            return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
        except:
            return link_limpo
    return link_limpo

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # 1. Trava de Segurança
    if not st.session_state.get("sel_nome"):
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")
        return

    nome_puro = st.session_state.sel_nome.replace("*", "").strip()
    link_orig = st.session_state.get("sel_link", "")
    mkt = st.session_state.get("mkt_global", "Shopee")
    link_rastreado = aplicar_id_afiliado(link_orig, mkt)

    with st.container(border=True):
        st.success(f"📦 **Alvo:** {nome_puro}")
        st.write(f"🔗 [ABRIR PRODUTO NA {mkt.upper()}]({link_rastreado})")

    # 2. SELEÇÃO DO ESTILO (Aqui a variável 'estilo' nasce)
    estilo = st.radio("Tom da Munição:", ["Agressivo", "Curioso", "Prático", "Autoridade"], horizontal=True)

    # 3. GERAÇÃO DA COPY (DENTRO DA FUNÇÃO - Resolve o NameError)
    if st.button(f"🔥 Gerar Munição {estilo}", use_container_width=True, key=f"btn_gen_{estilo}"):
        with st.spinner("🔱 Nexus moldando roteiros..."):
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            try:
                response = motor_ia_gemini.generate_content(prompt)
                if response and response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                    
                    # Salva no estado da sessão
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    
                    st.toast("✅ Munição Carregada!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro na IA: {e}")

    # 4. EXIBIÇÃO DAS COPIES
    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto)
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"env_est_{i}"):
                    st.session_state.copy_ativa = f"{texto}\n\n🛒 LINK: {link_rastreado}"
                    st.toast("Enviado ao Estúdio!")
