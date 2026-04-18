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
        if "http" not in raw_url: raw_url = "https://" + raw_url.lstrip(":/")
        return raw_url
    
    if "http" not in raw_url:
        raw_url = "https://shopee.com.br/" + raw_url.lstrip(":/")
    raw_url = raw_url.replace("http://", "https://")
    
    # 3. PROCESSAMENTO EXCLUSIVO SHOPEE
    if mkt == "Shopee":
        try:
            if "keyword=" in raw_url:
                termo = raw_url.split("keyword=")[1].split("&")[0]
                termo_codificado = urllib.parse.quote(termo)
                return f"https://shopee.com.br/search?keyword={termo_codificado}&smtt=0.0.{ID_FIXO_SHOPEE}"
            
            limpo = raw_url.split("?")[0].split("#")[0].rstrip("/")
            return f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
                
        except Exception as e:
            base = raw_url.split("?")[0].rstrip("/")
            return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
    
    return raw_url

def validar_link_shopee(link):
    if not link or link == "#": return False
    return "shopee" in str(link).lower() and "http" in str(link).lower()

def diagnosticar_erro_gemini(erro_mensagem):
    erro_lower = str(erro_mensagem).lower()
    if "404" in erro_lower:
        st.error("🔴 **Conexão Perdida:** O objeto da IA expirou. Clique em 'Resetar IA' na barra lateral.")
    elif "api key" in erro_lower:
        st.error("🔴 **Verifique sua GEMINI_API_KEY nos Secrets.**")
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
    
    # Limpa o nome para o prompt (remove asteriscos que a IA coloca)
    nome_puro = sel_nome.replace("*", "").strip()
    
    # Debug opcional
    with st.expander("🔍 Debug de Link"):
        st.code(f"Original: {link_original}\nMercado: {mkt}")
    
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    if not link_rastreado:
        st.error("❌ Link Inválido ou não capturado pelo Scanner.")
        return
    
    with st.container(border=True):
        st.success(f"📦 **Alvo Ativo:** {nome_puro}")
        
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

    # --- O BOTÃO AGORA ESTÁ DENTRO DA FUNÇÃO PARA RECONHECER O 'estilo' ---
    if st.button(f"🔥 Gerar Munição {estilo.upper()}", use_container_width=True, key=f"btn_gen_{estilo}"):
        with st.spinner(f"🔱 Nexus moldando roteiros de elite..."):
            # 1. Gera o prompt usando o nexus_copy.py
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            
            try:
                # 2. Chama o Gemini Pro
                response = motor_ia_gemini.generate_content(prompt)
                
                if response and response.text:
                    # 3. Limpa a resposta
                    resultado = nxcopy.limpar_copy(response.text)
                    
                    # 4. Processa versões separadas por ###
                    if "###" in resultado:
                        st.session_state.res_arsenal = [c.strip() for c in resultado.split("###") if len(c.strip()) > 20]
                    else:
                        st.session_state.res_arsenal = [resultado.strip()]
                    
                    st.toast("✅ Munição Carregada!")
                    st.rerun()
                else:
                    st.error("🔴 O Gemini retornou uma resposta vazia.")
            except Exception as e:
                diagnosticar_erro_gemini(e)

    # --- EXIBIÇÃO DAS COPIES ---
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
