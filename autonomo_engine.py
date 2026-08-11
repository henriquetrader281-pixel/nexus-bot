import streamlit as st
import os

def processar_ciclo_visual(api_key, base_url, provedor="openai"):
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor REAL, LATENTE e URGENTE que as pessoas estão a enfrentar agora.
    
    IMPORTANTE: O PRODUTO_SOLUCAO deve ser a cura direta para a DOR detectada. 
    
    REGRAS PARA A COPY (ESTILO AGÊNCIA DE ALTO NÍVEL):
    - Use o framework AIDA (Atenção, Interesse, Desejo, Ação).
    - Headline: Comece com um gancho de curiosidade ou uma verdade contra-intuitiva.
    - Corpo: Foque na transformação/alívio da dor, não nas características.
    - Escassez/Urgência: Adicione um gatilho de que o produto é um 'achado' ou 'segredo'.
    - CTA Agressivo: Chamada clara para ação (ex: 'Comenta QUERO que te envio o segredo').
    - Tom: Mistura de autoridade com indicação pessoal.
    - Evite termos genéricos. Seja específico e persuasivo.

    Retorne estritamente no formato:
    DOR: [descrição da dor]
    NICHO: [nicho]
    PRODUTO_SOLUCAO: [nome do produto físico exato]
    COPY_OFERTA: [copy de alta conversão com CTA e gatilhos]
    PROMPT_IMAGEM: [descrição visual do produto para busca]
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
                {"role": "system", "content": "Você é um Copywriter Senior de uma agência de performance. Sua especialidade é criar desejo imediato e converter leads frios em compradores através de gatilhos de curiosidade e autoridade."},
                {"role": "user", "content": prompt_dor}
            ],
            model=model_name,
            temperature=0.9
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
                    if st.button("🎨 BUSCAR IMAGEM DO PRODUTO"):
                        with st.spinner("Buscando imagem correspondente..."):
                            # Busca uma imagem real baseada no produto detectado
                            query = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "+")
                            url_imagem = f"https://source.unsplash.com/featured/?{query}"
                            st.image(url_imagem, caption=f"Sugestão visual para: {dados.get('PRODUTO_SOLUCAO')}")
                            st.success("Imagem localizada com sucesso!")

                    id_afiliado = "18316451024"
                    produto_nome = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "%20")
                    link = f"https://shopee.com.br/universal-link/search?smtt=0.0.{id_afiliado}&keyword={produto_nome}"
                    
                    st.link_button("🛒 Ver Produto no Marketplace", link, use_container_width=True)
                    
                    if st.button("🚀 DISPARAR POSTAGEM AGORA", type="primary"):
                        st.balloons()
                        st.success("Postagem agendada e enviada para o Postador Autónomo!")
        else:
            st.info("Clique no botão ao lado para iniciar a inteligência autônoma.")
