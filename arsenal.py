import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re

def aplicar_id_afiliado(link, mkt):
    """
    Processa link do produto e adiciona ID afiliado Shopee (18316451024).
    Garante o rastro fixo e a saída do domínio do Nexus.
    """
    ID_FIXO_SHOPEE = "18316451024"
    
    if not link or len(str(link)) < 5: 
        return None
    
    # 1. LIMPEZA RADICAL: Remove lixo da IA com Regex
    raw_url = str(link).split("###")[0].split("\n")[0].strip()
    raw_url = re.sub(r'[\*\t\r]', '', raw_url) # Remove asteriscos e tabs
    raw_url = raw_url.replace(" ", "").strip()
    
    # 2. VALIDAÇÃO E PROTOCOLO
    if "shopee" not in raw_url.lower():
        # Se for Mercado Livre ou Amazon, apenas limpa e retorna
        if "http" not in raw_url: raw_url = "https://" + raw_url.lstrip(":/")
        return raw_url
    
    # Força HTTPS absoluto para evitar "apontar para o nexus"
    if "http" not in raw_url:
        raw_url = "https://shopee.com.br/" + raw_url.lstrip(":/")
    raw_url = raw_url.replace("http://", "https://")
    
    # 3. PROCESSAMENTO EXCLUSIVO SHOPEE
    if mkt == "Shopee":
        try:
            # CASO A: Link de busca com keyword
            if "keyword=" in raw_url:
                termo = raw_url.split("keyword=")[1].split("&")[0]
                termo_codificado = urllib.parse.quote(termo)
                return f"https://shopee.com.br/search?keyword={termo_codificado}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            # CASO B: Link direto de produto
            limpo = raw_url.split("?")[0].split("#")[0].rstrip("/")
            return f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
                
        except Exception as e:
            # Fallback seguro
            base = raw_url.split("?")[0].rstrip("/")
            return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
    
    return raw_url

def validar_link_shopee(link):
    if not link or link == "#": return False
    return "shopee" in str(link).lower() and "http" in str(link).lower()

def diagnosticar_erro_gemini(erro_mensagem):
    """Analisa erro do Gemini e exibe solução específica."""
    erro_lower = str(erro_mensagem).lower()
    if "404" in erro_lower or "not found" in erro_lower:
        st.error("🔴 **ERRO 404: Modelo Gemini não encontrado**\n\nNo seu `app.py`, use: `genai.GenerativeModel('gemini-1.5-flash')` (Sem o models/)")
    elif "api key" in erro_lower or "401" in erro_lower:
        st.error("🔴 **ERRO DE AUTENTICAÇÃO: API Key Inválida**")
    else:
        st.error(f"🔴 **Erro na IA:** {erro_mensagem}")

def exibir_arsenal(miny, motor_ia_gemini):
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    
    # Debug opcional para o Henrique
    with st.expander("🔍 Debug de Link"):
        st.code(f"Original: {link_original}\nMercado: {mkt}")
    
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    if not link_rastreado:
        st.error("❌ Link Inválido ou não capturado pelo Scanner.")
        return
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        
        # LINK HTML BLINDADO (Abre em nova aba)
        st.write(
            f'🔗 **Munição Pronta:** '
            f'<a href="{link_rastreado}" target="_blank" rel="noopener noreferrer" '
            f'style="color: #FF4B4B; text-decoration: none; font-weight: bold; '
            f'border: 2px solid #FF4B4B; padding: 8px 12px; border-radius: 5px; '
            f'display: inline-block;">'
            f'ABRIR PRODUTO NA {mkt.upper()} 🚀</a>',
            unsafe_allow_html=True
        )
        st.caption(f"🔐 Rastreado com ID: `{link_rastreado}`")
        
        musica = st.session_state.get("musica_selecionada")
        if musica: st.info(f"🎵 **Áudio Viral:** {musica}")

    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True)

    if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
        with st.spinner("Gemini moldando roteiros de elite..."):
            try:
                prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
                response = motor_ia_gemini.generate_content(prompt)
                if response.text:
                    resultado = nxcopy.limpar_copy(response.text)
                    st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 15]
                    st.rerun()
            except Exception as e:
                diagnosticar_erro_gemini(e)

    if st.session_state.get("res_arsenal"):
        st.divider()
        for i, texto_copy in enumerate(st.session_state.res_arsenal[:3]):
            with st.container(border=True):
                st.markdown(f"#### 💎 Munição V{i+1}")
                st.write(texto_copy)
                if st.button(f"🎬 Enviar V{i+1} ao Estúdio", key=f"btn_env_{i}", use_container_width=True):
                    st.session_state.copy_ativa = f"{texto_copy}\n\n🛒 LINK: {link_rastreado}"
                    st.session_state.link_final_afiliado = link_rastreado
                    st.toast("Enviado ao Estúdio!")
