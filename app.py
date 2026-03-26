import streamlit as st
from groq import Groq
from datetime import datetime
import pandas as pd # Precisará adicionar 'pandas' no requirements.txt
import io

# --- 1. CONFIGURAÇÕES E SECRETS ---
api_key = st.secrets.get("GROQ_API_KEY")
st.set_page_config(page_title="Nexus Bot: Multicanal", page_icon="🌐", layout="wide")

# --- 2. CONEXÃO COM A IA ---
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro na conexão Groq: {e}")
else:
    st.error("API Key da Groq não encontrada.")

def gerar_ia(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# Função para sanitizar nomes de arquivos e chaves
def sanitizar(texto):
    return "".join(c for c in texto if c.isalnum() or c in (' ', '_')).rstrip()

# --- 3. NAVEGAÇÃO POR ABAS ---
st.title("🌐 Nexus Brain: Hub Multicanal Pro")
st.caption(f"📅 Data da Operação: {datetime.now().strftime('%d/%m/%Y')}")

aba_hub, aba_midia, aba_social, aba_lucro = st.tabs([
    "🔎 Hub de Mineração", 
    "🎥 Busca de Mídia & Fonte",
    "📅 Agendador Social", 
    "📊 Métricas de Lucro"
])

# --- ABA 1: HUB DE MINERAÇÃO (MULTICANAL + DATA) ---
with aba_hub:
    st.header("🔎 Inteligência de Mercado Diária (Shopee, ML, Amazon)")
    
    col_ref, col_btn = st.columns([3, 1])
    # col_ref.write(f"📅 **Data da Varredura:** {datetime.now().strftime('%d/%m/%Y')}")
    
    if col_btn.button("Atualizar Mineração Global Hoje", key="btn_min_global"):
        with st.status("Nexus varrendo tendências multicanal...", expanded=True) as status:
            prompt_hub = f"""
            Aja como um Meta-Scanner de E-commerce Pro em Março de 2026. 
            Liste os 10 produtos mais virais e de alta conversão hoje, analisando Shopee Brasil, Mercado Livre e Amazon Brasil. 
            Responda EXATAMENTE em formato de tabela Markdown, sem texto extra, com as colunas:
            | Produto | Plataforma Principal | Nota Viral (0-10) | Link de Referência (Shopee/ML/Amazon) |
            | --- | --- | --- | --- |
            Use links reais ou de busca precisos para o mercado brasileiro.
            """
            res = gerar_ia(prompt_hub)
            st.session_state['tabela_minerada'] = res
            status.update(label="Tabela Multicanal Atualizada!", state="complete", expanded=False)
    
    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'], unsafe_allow_html=True)
        st.caption("💡 Dica: Copie o nome do produto que deseja explorar e vá para a aba 'Busca de Mídia'.")

# --- ABA 2: BUSCA DE MÍDIA & FONTE DE DADOS (NOVO!) ---
with aba_midia:
    st.header("🎥 Busca de Mídia & Fonte de Dados")
    st.markdown("Copie o nome exato do produto da aba 'Hub' para buscar fontes de vídeo/imagem para sua automação.")
    
    prod_busca = st.text_input("Nome do Produto para Mídia:", placeholder="Ex: Mini Projetor Portátil Hy300")
    source_lang = st.radio("Idioma da Fonte:", ["Português (Brasil)", "Inglês (Global/China)"])

    if st.button("Buscar Fontes de Mídia (Vídeos/Imagens)"):
        if client and prod_busca:
            with st.spinner(f"O Nexus está varrendo fontes de mídia para '{prod_busca}'..."):
                # Prompt para gerar links de busca precisos para mídia
                prompt_midia = f"""
                Gere uma lista organizada de links de busca diretos para encontrar vídeos e imagens de alta qualidade para o produto: '{prod_busca}' em {source_lang}.
                Aja como um curador de conteúdo para automação de dropshipping.
                Gere buscas para: TikTok, Instagram Reels, YouTube Shorts, AliExpress (página de feedback de imagem) e Pinterest.
                Responda com Markdown organizado por plataforma.
                """
                res_midia = gerar_ia(prompt_midia)
                st.session_state['fontes_midia'] = res_midia
                st.success("Fontes Encontradas!")
                st.markdown(st.session_state['fontes_midia'])
                
                # Armazena o produto selecionado para o roteiro
                st.session_state['produto_selecionado'] = prod_busca

    st.divider()
    
    # Seção de Roteiro Integrada
    if 'produto_selecionado' in st.session_state:
        st.subheader(f"📝 Criador de Conteúdo: {st.session_state['produto_selecionado']}")
        if st.button("Gerar Roteiro Viral + Estrutura de Cenas"):
            with st.spinner("O Nexus está redigindo o conteúdo magnético..."):
                prompt_full = f"""
                Crie um roteiro de 30s para '{st.session_state['produto_selecionado']}' (Hook, Problema, Solução, CTA) e divida em cenas de 3s para o editor, focando no estilo viral do TikTok/Reels.
                """
                roteiro = gerar_ia(prompt_full)
                st.session_state['roteiro_final'] = roteiro
                st.success("Roteiro pronto!")
                st.write(roteiro)
    else:
        st.info("⚠️ Busque a mídia de um produto acima para habilitar o criador de roteiro.")

# --- ABA 3: AGENDADOR SOCIAL (O QUE JÁ FUNCIONA) ---
with aba_social:
    st.header("📅 Agendamento Inteligente")
    
    if 'roteiro_final' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            rede = st.selectbox("Destino do Post:", ["Instagram Reels", "TikTok", "YouTube Shorts"])
            horario = st.select_slider("Melhor Horário Sugerido:", options=["09:00", "12:00", "18:00", "21:00"])
        
        with col2:
            legenda_estilo = st.radio("Estilo da Legenda:", ["Urgência", "Curiosidade", "Engraçada"])
            if st.button("Gerar Legenda p/ Rede Social"):
                with st.spinner("Gerando legenda..."):
                    legenda = gerar_ia(f"Crie uma legenda {legenda_estilo} com hashtags para: {st.session_state['roteiro_final']}")
                    st.session_state['legenda_final'] = legenda

        if 'legenda_final' in st.session_state:
            st.text_area("Legenda Gerada:", st.session_state['legenda_final'], height=100)

        if st.button("🚀 Confirmar Agendamento no Nexus", use_container_width=True):
            st.balloons()
            # Simulando a Fila de Postagem
            if 'fila' not in st.session_state: st.session_state['fila'] = []
            st.session_state['fila'].append({
                "Produto": st.session_state.get('produto_selecionado', 'N/A'),
                "Rede": rede, 
                "Hora": horario, 
                "Status": "Agendado"
            })
            st.success(f"Post agendado para '{st.session_state.get('produto_selecionado')}' em {rede} às {horario}!")
    else:
        st.warning("⚠️ Gere um roteiro na aba anterior para habilitar o agendador.")

    if 'fila' in st.session_state:
        st.divider()
        st.subheader("📋 Fila de Postagens Ativa")
        st.table(st.session_state['fila'])

# --- ABA 4: MÉTRICAS E LUCRO (O QUE JÁ FUNCIONA) ---
with aba_lucro:
    st.header("📊 Painel de Performance Multicanal")
    m1, m2, m3 = st.columns(3)
    m1.metric("Alcance Estimado (Shopee/ML/Amz)", "25.100", "+18%")
    m2.metric("Conversão Média", "3.4%", "+1.1%")
    m3.metric("Lucro Líquido Acumulado (Mês)", "R$ 4.312", "+R$ 510")

    st.divider()
    st.subheader("💰 Calculadora de ROI Pro")
    col_pl, col_v, col_c = st.columns(3)
    plataforma = col_pl.selectbox("Plataforma do Produto:", ["Shopee (18% taxa)", "Mercado Livre (22% taxa)", "Amazon (15% taxa)"])
    venda = col_v.number_input("Preço de Venda (R$):", value=79.90)
    custo = col_c.number_input("Custo + Frete (R$):", value=35.00)
    
    if st.button("Calcular Lucratividade Multicanal"):
        # Cálculo Dinâmico de Taxas
        taxa = 0.18
        if "Mercado Livre" in plataforma: taxa = 0.22
        elif "Amazon" in plataforma: taxa = 0.15
        
        lucro_real = venda - custo - (venda * taxa)
        st.metric("Lucro Líquido por Unidade", f"R$ {lucro_real:.2f}", delta=f"Margem: {(lucro_real/venda)*100:.1f}%")
        
        if lucro_real > 25:
            st.success(f"🔥 Produto Altamente Lucrativo na {plataforma}! Escalar automação de vídeos.")
        else:
            st.warning(f"⚠️ Margem apertada na {plataforma}. Verifique os custos.")
