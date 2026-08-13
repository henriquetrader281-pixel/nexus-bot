import streamlit as st
import os

def processar_ciclo_visual(api_key, base_url, provedor="openai"):
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor REAL, LATENTE e URGENTE que as pessoas estão a enfrentar agora.
    
    IMPORTANTE: O PRODUTO_SOLUCAO deve ser a cura direta para a DOR detectada. 
    
    REGRAS RÍGIDAS PARA A COPY (ESTILO AGÊNCIA DE PERFORMANCE + CTA OBRIGATÓRIO):
    - Use o framework AIDA (Atenção, Interesse, Desejo, Ação).
    - Hook / Gancho Inicial (Primeiros 3 segundos): Frase altamente curiosa ou contra-intuitiva para parar o scroll.
    - Corpo: Foque na transformação e alívio imediato da dor.
    - CTA OBRIGATÓRIO E EXPLICÍCITO: Termine obrigatoriamente com uma Chamada para Ação irresistível (ex: 'Clica no link da bio ou comenta QUERO para garantir o teu com desconto exclusivo no Mercado Livre!').

    Retorne estritamente no formato exato:
    DOR: [descrição detalhada da dor]
    NICHO: [nicho]
    PRODUTO_SOLUCAO: [nome do produto físico exato]
    COPY_OFERTA: [copy completa com gancho, corpo AIDA e CTA agressivo]
    PROMPT_IMAGEM: [descrição visual cinematográfica do produto em uso para geração por IA]
    """
    
    try:
        if provedor == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt_dor)
            return response.text.strip()
        elif provedor == "groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            model_name = "llama-3.3-70b-versatile"
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_dor}],
                model=model_name,
                temperature=0.9
            )
            return chat.choices[0].message.content.strip()
        else:
            from openai import OpenAI
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = OpenAI(**client_kwargs)
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_dor}],
                model="gpt-4o-mini",
                temperature=0.9
            )
            return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def exibir_aba_autonomo():
    st.header("🤖 Nexus Autônomo: Sincronização & Funil Completo")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.info("💡 **Fluxo Sincronizado:** Ao gerar um ciclo, o Nexus deteta a dor, alimenta o motor SEO (Ubersuggest) e envia a média diretamente para a aba 'Estúdio'.")
        
        provedor = st.radio("Selecione o Provedor de IA:", ["ChatGPT (OpenAI)", "Google Gemini", "Groq"], horizontal=True)
        
        if st.button("🚀 INICIAR CICLO AUTÔNOMO", use_container_width=True):
            if provedor == "Google Gemini":
                api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
                base_url = None
                p_nome = "gemini"
            elif provedor == "Groq":
                api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
                base_url = None
                p_nome = "groq"
            else:
                api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
                base_url = st.secrets.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
                p_nome = "openai"
            
            if not api_key:
                st.error(f"Chave de API para {provedor} não encontrada nos Secrets!")
            else:
                with st.spinner(f"IA Nexus ({provedor}) a cruzar dores, SEO e Ganchos Virais..."):
                    resultado = processar_ciclo_visual(api_key, base_url, p_nome)
                    st.session_state.resultado_autonomo = resultado
                    st.success("Ciclo sincronizado com sucesso!")

    with col1:
        if "resultado_autonomo" in st.session_state:
            res = st.session_state.resultado_autonomo
            if "Erro:" in res:
                st.error(res)
            else:
                linhas = res.split('\n')
                dados = {}
                chave_atual = None
                valor_atual = []
                
                for linha in linhas:
                    if ":" in linha and any(linha.startswith(k) for k in ["DOR", "NICHO", "PRODUTO_SOLUCAO", "COPY_OFERTA", "PROMPT_IMAGEM"]):
                        if chave_atual:
                            dados[chave_atual] = "\n".join(valor_atual).strip()
                        partes = linha.split(":", 1)
                        chave_atual = partes[0].strip()
                        valor_atual = [partes[1].strip()]
                    elif chave_atual:
                        valor_atual.append(linha)
                if chave_atual:
                    dados[chave_atual] = "\n".join(valor_atual).strip()
                
                # Sincronização automática com session_state para SEO e Estúdio
                st.session_state.sel_nome = dados.get('PRODUTO_SOLUCAO', 'Produto Exemplo')
                st.session_state.sel_dor = dados.get('DOR', 'Necessidade do mercado')
                st.session_state.ultima_copy = dados.get('COPY_OFERTA', '---')
                
                with st.container(border=True):
                    st.subheader(f"🎯 Foco: {dados.get('NICHO', 'Mercado Geral')}")
                    st.warning(f"**DOR DETECTADA:** {dados.get('DOR', '---')}")
                    st.success(f"**PRODUTO SOLUÇÃO:** {dados.get('PRODUTO_SOLUCAO', '---')}")
                    
                    st.markdown("### 📝 Copy de Alta Conversão (Com Hook, AIDA & CTA)")
                    st.code(dados.get('COPY_OFERTA', '---'), language="text")
                    
                    st.markdown("### 🖼️ Envio para o Estúdio & Mídia")
                    if st.button("🚀 GERAR MÉDIA E ENVIAR PARA O ESTÚDIO", key="btn_send_estudio", type="primary"):
                        with st.spinner("Gerando criativo e sincronizando com o Estúdio..."):
                            query = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "+")
                            url_img = f"https://source.unsplash.com/featured/?{query}"
                            st.session_state.nexus_media_url = url_img
                            st.session_state.nexus_media_ready = True
                            st.success("Mídia gerada e sincronizada com sucesso! Vá à aba 'ESTÚDIO' para visualizar e exportar.")
                    
                    st.markdown("### 🛒 Funil de Afiliados (Mercado Livre / Shopee)")
                    mkt_escolhido = st.selectbox("Escolha a Vitrine:", ["Mercado Livre", "Shopee", "Amazon"], key=f"mkt_{hash(res)}")
                    
                    p_nome_url = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "%20")
                    if mkt_escolhido == "Mercado Livre":
                        link = f"https://lista.mercadolivre.com.br/{p_nome_url}_NoIndex_True"
                    elif mkt_escolhido == "Amazon":
                        link = f"https://www.amazon.com.br/s?k={p_nome_url}&tag=nexusbot-20"
                    else:
                        link = f"https://shopee.com.br/universal-link/search?keyword={p_nome_url}"
                    
                    st.link_button(f"🛒 Ver no {mkt_escolhido} (Link Blindado)", link, use_container_width=True)
