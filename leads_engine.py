import streamlit as st
import random

def minerar_leads_intencao(nicho):
    """
    Simula a busca em redes sociais (Twitter/X, Reddit, Fóruns) por pessoas
    que expressam desejo de compra ou problemas específicos.
    """
    
    # Base de "Gatilhos de Intenção" que o bot procuraria via API
    gatilhos = [
        "alguém sabe onde comprar",
        "preciso de uma recomendação de",
        "qual o melhor custo benefício para",
        "estou cansado de",
        "alguém já testou o",
        "vale a pena comprar"
    ]
    
    # Simulação de leads reais encontrados
    leads_base = {
        "Casa": [
            {"user": "@marcos_silva", "plataforma": "Twitter", "texto": "Alguém sabe onde comprar um robô aspirador que não bata em tudo? O meu é horrível."},
            {"user": "u/ana_decor", "plataforma": "Reddit", "texto": "Preciso de uma recomendação de luminária para home office que não canse a vista."},
        ],
        "Produtividade": [
            {"user": "@tech_lucas", "plataforma": "Twitter", "texto": "Qual o melhor custo benefício para um teclado mecânico silencioso? Trabalho à noite."},
            {"user": "u/dev_junior", "plataforma": "Reddit", "texto": "Estou cansado de fones que machucam a orelha depois de 2 horas de call."},
        ],
        "Eletrónicos": [
            {"user": "@gamer_br", "plataforma": "Twitter", "texto": "Vale a pena comprar aquele projetor portátil da Shopee? Quero fazer um cinema no quarto."},
            {"user": "u/vlog_maker", "plataforma": "Reddit", "texto": "Alguém já testou aquele microfone de lapela sem fio barato? Preciso pra gravar vídeos."},
        ]
    }
    
    # Busca o nicho ou retorna um padrão
    leads = leads_base.get(nicho, leads_base["Casa"])
    return random.choice(leads)

def exibir_aba_leads():
    st.header("🎯 Radar de Leads: Intenção de Compra")
    st.markdown("---")
    
    nicho = st.selectbox("Selecione o Nicho para Minerar Leads:", ["Casa", "Produtividade", "Eletrónicos"])
    
    if st.button("🔍 VARRER REDES SOCIAIS POR LEADS", use_container_width=True):
        with st.spinner(f"Escaneando Twitter e Reddit para o nicho {nicho}..."):
            lead = minerar_leads_intencao(nicho)
            st.session_state.lead_atual = lead
            st.success("Lead com alta intenção de compra localizado!")

    if "lead_atual" in st.session_state:
        lead = st.session_state.lead_atual
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"### {lead['plataforma']}")
            with c2:
                st.markdown(f"**Usuário:** {lead['user']}")
                st.write(f"💬 *\"{lead['texto']}\"*")
            
            st.divider()
            st.markdown("### 🤖 Sugestão de Abordagem Autónoma")
            
            # Gerar uma resposta humanizada
            prompt_resposta = f"O usuário {lead['user']} disse: '{lead['texto']}'. Sugira uma resposta curta, amigável e não robótica que ajude ele e mencione que você achou um produto perfeito."
            
            if st.button("🪄 GERAR RESPOSTA HUMANIZADA"):
                # Aqui usaríamos a IA para gerar a resposta
                st.info("Sugestão: 'Oi! Vi que você está procurando por isso. Eu tive o mesmo problema e esse aqui salvou meu setup, dá uma olhada no link da bio!'")
            
            st.button("🚀 ENVIAR RESPOSTA AUTOMÁTICA (SIMULAÇÃO)", type="primary")
