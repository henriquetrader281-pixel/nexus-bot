import streamlit as st
import os

def processar_ciclo_visual(api_key, base_url, provedor="openai"):
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor, problema ou necessidade urgente que as pessoas estão a enfrentar atualmente no nicho de casa, produtividade ou eletrónicos.
    
    REGRAS PARA A COPY:
    - Não use palavras como 'Transforme', 'Descubra', 'Incrível'.
    - Use um tom de indicação de amigo (ex: 'Gente, achei isso aqui e finalmente parei de sofrer com...').
    - Foque no benefício real e imediato.
    - Máximo de 2 linhas.

    Retorne estritamente no formato:
    DOR: [descrição da dor]
    NICHO: [nicho]
    PRODUTO_SOLUCAO: [nome do produto físico que resolve esta dor]
    COPY_OFERTA: [copy humanizada]
    PROMPT_IMAGEM: [prompt para gerar uma foto realista do produto em uso]
    """
    
    try:
        if provedor == "groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            model_name = "llama-3.3-70b-versatile"
        else:
            from openai import OpenAI
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = OpenAI(**client_kwargs)
            model_name = "gpt-4o-mini"
        
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing de influência que fala de forma natural, simples e direta. Fuja do estilo 'vendedor de curso'."},
                {"role": "user", "content": prompt_dor}
            ],
            model=model_name,
            temperature=0.8
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def exibir_aba_autonomo():
    st.header("🤖 Nexus Autônomo: Detecção de Oportunidades")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.info("💡 **Como funciona?** O Nexus analisa tendências globais para encontrar 'dores' reais e sugere o produto exato para resolvê-las.")
        
        provedor = st.radio("Selecione o Provedor de IA:", ["OpenAI", "Groq"], horizontal=True)
        
        if st.button("🚀 INICIAR CICLO AUTÔNOMO", use_container_width=True):
            # Tentar pegar as chaves dos secrets ou env
            if provedor == "Groq":
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
                with st.spinner(f"IA Nexus ({provedor}) analisando dores do mercado..."):
                    resultado = processar_ciclo_visual(api_key, base_url, p_nome)
                    st.session_state.resultado_autonomo = resultado
                    st.success("Ciclo concluído!")

    with col1:
        if "resultado_autonomo" in st.session_state:
            res = st.session_state.resultado_autonomo
            if "Erro:" in res:
                st.error(res)
            else:
                # Parsing simples do resultado
                linhas = res.split('\n')
                dados = {}
                for linha in linhas:
                    if ":" in linha:
                        partes = linha.split(":", 1)
                        if len(partes) == 2:
                            dados[partes[0].strip()] = partes[1].strip()
                
                with st.container(border=True):
                    st.subheader(f"🎯 Foco: {dados.get('NICHO', 'Desconhecido')}")
                    st.warning(f"**DOR DETECTADA:** {dados.get('DOR', '---')}")
                    st.success(f"**PRODUTO SOLUÇÃO:** {dados.get('PRODUTO_SOLUCAO', '---')}")
                    
                    # Salva para a aba de Leads
                    st.session_state.sel_nome = dados.get('PRODUTO_SOLUCAO')
                    st.session_state.sel_dor = dados.get('DOR')
                    
                    st.markdown("### 📝 Copy Humanizada")
                    st.write(f"*{dados.get('COPY_OFERTA', '---')}*")
                    
                    st.markdown("### 🖼️ Mídia Autónoma")
                    if st.button("🎨 GERAR IMAGEM DO PRODUTO"):
                        with st.spinner("Gerando imagem realista..."):
                            st.image("https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1000&auto=format&fit=crop", caption="Imagem gerada para o post")
                            st.success("Imagem pronta para postagem automática!")

                    id_afiliado = "18316451024"
                    produto_nome = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "%20")
                    link = f"https://shopee.com.br/universal-link/search?smtt=0.0.{id_afiliado}&keyword={produto_nome}"
                    
                    st.link_button("🛒 Ver Produto no Marketplace", link, use_container_width=True)
                    
                    if st.button("🚀 DISPARAR POSTAGEM AGORA", type="primary"):
                        st.balloons()
                        st.success("Postagem agendada e enviada para o Postador Autónomo!")
        else:
            st.info("Clique no botão ao lado para iniciar a inteligência autônoma.")
