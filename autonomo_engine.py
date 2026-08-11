import streamlit as st
import os
from openai import OpenAI

def processar_ciclo_visual(openai_api_key, openai_base_url):
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor, problema ou necessidade urgente que as pessoas estão a enfrentar atualmente no nicho de casa, produtividade ou eletrónicos.
    Retorne estritamente no formato:
    DOR: [descrição da dor]
    NICHO: [nicho]
    PRODUTO_SOLUCAO: [nome do produto físico que resolve esta dor]
    COPY_OFERTA: [uma copy persuasiva de 2 linhas focada na dor, com chamada para ação e espaço para link]
    """
    
    try:
        client_kwargs = {"api_key": openai_api_key}
        if openai_base_url:
            client_kwargs["base_url"] = openai_base_url
        client = OpenAI(**client_kwargs)
        
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um analista de mercado e especialista em copywriting de conversão."},
                {"role": "user", "content": prompt_dor}
            ],
            model="gemini-3-flash-preview",
            temperature=0.7
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
        if st.button("🚀 INICIAR CICLO AUTÔNOMO", use_container_width=True):
            # Tentar pegar as chaves dos secrets ou env
            api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            base_url = st.secrets.get("OPENAI_API_BASE") or os.environ.get("OPENAI_API_BASE")
            
            if not api_key:
                st.error("Chave de API não encontrada nos Secrets!")
            else:
                with st.spinner("IA Nexus analisando dores do mercado..."):
                    resultado = processar_ciclo_visual(api_key, base_url)
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
                        k, v = linha.split(":", 1)
                        dados[k.strip()] = v.strip()
                
                with st.container(border=True):
                    st.subheader(f"🎯 Foco: {dados.get('NICHO', 'Desconhecido')}")
                    st.warning(f"**DOR DETECTADA:** {dados.get('DOR', '---')}")
                    st.success(f"**PRODUTO SOLUÇÃO:** {dados.get('PRODUTO_SOLUCAO', '---')}")
                    
                    st.markdown("### 📝 Copy Gerada")
                    st.code(dados.get('COPY_OFERTA', '---'), language="text")
                    
                    id_afiliado = "18316451024"
                    produto_nome = dados.get('PRODUTO_SOLUCAO', 'produto').replace(" ", "%20")
                    link = f"https://shopee.com.br/universal-link/search?smtt=0.0.{id_afiliado}&keyword={produto_nome}"
                    
                    st.link_button("🛒 Ver Produto no Marketplace", link, use_container_width=True)
        else:
            st.info("Clique no botão ao lado para iniciar a inteligência autônoma.")
