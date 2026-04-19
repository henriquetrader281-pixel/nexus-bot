import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re
import random

def aplicar_id_afiliado(link, mkt):
    """
    Processa link do produto e adiciona ID afiliado Shopee (18316451024).
    """
    ID_FIXO_SHOPEE = "18316451024"
    if not link or len(str(link)) < 5: 
        return None
    
    raw_url = str(link).split("###")[0].split("\n")[0].strip()
    raw_url = re.sub(r'[\*\t\r]', '', raw_url)
    raw_url = raw_url.replace(" ", "").strip()
    
    if "shopee" not in raw_url.lower():
        if "http" not in raw_url: raw_url = "https://" + raw_url.lstrip(":/")
        return raw_url
    
    if "http" not in raw_url:
        raw_url = "https://shopee.com.br/" + raw_url.lstrip(":/")
    
    if mkt == "Shopee":
        try:
            if "keyword=" in raw_url:
                termo = raw_url.split("keyword=")[1].split("&")[0]
                termo_codificado = urllib.parse.quote(termo)
                return f"https://shopee.com.br/search?keyword={termo_codificado}&smtt=0.0.{ID_FIXO_SHOPEE}"
            limpo = raw_url.split("?")[0].split("#")[0].rstrip("/")
            return f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
        except:
            base = raw_url.split("?")[0].rstrip("/")
            return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
    return raw_url

def exibir_arsenal(miny, motor_ia_gemini):
    # HEADER PREMIUM COM GRADIENTE
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 1px solid #3b82f6;">
            <h2 style="color: white; margin: 0;">🔱 ARSENAL NEXUS ABSOLUTE</h2>
            <p style="color: #94a3b8; font-size: 0.9em;">Munições de Alta Conversão | Framework AIDA Ativo</p>
        </div>
    """, unsafe_allow_html=True)
    
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    nome_puro = sel_nome.replace("*", "").strip()
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success(f"📦 **Alvo Ativo:** {nome_puro}")
            st.caption(f"🔐 Rastreio Shopee: `18316451024` Ativo")
        with col2:
            st.write(f"🔗 [ABRIR NA {mkt.upper()}]({link_rastreado})")

    st.divider()
    estilo = st.radio("Tom da Munição:", ["agressivo", "curioso", "prático", "autoridade"], horizontal=True, key="radio_arsenal")

    if st.button(f"🚀 FORJAR MUNIÇÃO {estilo.upper()} (ALTO IMPACTO)", use_container_width=True, type="primary"):
        with st.spinner("🔱 Nexus moldando munição de elite..."):
            prompt = nxcopy.gerar_prompt_aida(nome_puro, estilo=estilo)
            try:
                if hasattr(motor_ia_gemini, 'chat'): # Groq
                    chat_completion = motor_ia_gemini.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    texto_gerado = chat_completion.choices[0].message.content
                else: # Gemini
                    response = motor_ia_gemini.generate_content(prompt)
                    texto_gerado = response.text

                if texto_gerado:
                    st.session_state.res_arsenal = [texto_gerado]
                    st.rerun()
            except Exception as e:
                st.error(f"Erro na geração: {e}")

    # --- EXIBIÇÃO DAS COPIES PREMIUM ---
    if st.session_state.get("res_arsenal"):
        conteudo_ia = st.session_state.res_arsenal[0] if isinstance(st.session_state.res_arsenal, list) else st.session_state.res_arsenal
        lista_copies = [c.strip() for c in conteudo_ia.split("###") if len(c.strip()) > 10]

        # Banco de CTAs do arquivo BANCO_CTAS_MATADORAS.md
        ctas_premium = [
            "🎬 ⚡ ENVIAR V{n} AO ESTÚDIO AGORA ⚡",
            "🚀 DETONAR ESTA MUNIÇÃO JÁ (+ R$450 em vendas)",
            "💰 ENVIAR V{n} → GERAR R$85+ JÁ HOJE",
            "🎯 ATIVAR V{n} AGORA (ALTA CONVERSÃO)"
        ]

        for i, texto_bruto in enumerate(lista_copies):
            texto_limpo = nxcopy.limpar_copy(texto_bruto)
            cta_final = random.choice(ctas_premium).format(n=i+1)
            
            with st.container(border=True):
                # Badge de Potência (Conforme ESTRATEGIA_MARKETING_PREMIUM)
                st.markdown(f"✨ **MUNIÇÃO ELITE V{i+1}** | ⚡ `POTÊNCIA 98%` | 📈 `ROI EST. 4.5x` ")
                st.write(texto_limpo)
                
                if st.button(cta_final, key=f"btn_env_{i}", use_container_width=True, type="primary"):
                    st.session_state.copy_ativa = f"{texto_limpo}\n\n🛒 LINK: {link_rastreado}"
                    st.session_state.link_final_afiliado = link_rastreado
                    st.balloons()
                    st.toast(f"🔥 Munição V{i+1} detonada e enviada ao Estúdio!")
