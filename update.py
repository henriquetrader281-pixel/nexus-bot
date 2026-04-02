import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os

# Puxamos a função de IA do app principal para economizar tokens e memória
from app import gerar_ia 

DATA_PATH = "dataset_nexus.csv"

def aplicar_seo_viral(produto, link_base, nicho):
    """
    CONSOLIDAÇÃO V1-V73:
    - Escala 10x (V72)
    - Sub_ID Tracking (V71)
    - Ganchos de SEO Viral (V73)
    - Roteiros Automáticos (V70)
    - Horários de Pico Brasília (V72)
    """
    # Configurações de SEO & Tempo
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    hashtags = ["#achadinhos", "#shopee", "#viral", "#utilidades", "#comprinhas"]
    horarios = ["11:15", "12:45", "17:30", "18:50", "20:10", "21:30", "22:45", "08:30", "15:00", "19:55"]

    try:
        # 1. Recupera ID de Afiliado dos Secrets
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        df = pd.read_csv(DATA_PATH)
        novas = []

        # 2. IA GERA 10 ROTEIROS DE UMA VEZ (Estratégia V70)
        prompt_roteiros = f"""
        Aja como Diretor de Vídeos Curtos. Crie 10 roteiros de 15 segundos para {produto} no nicho {nicho}.
        Cada roteiro deve ter: Gancho Inicial + Demonstração + Chamada de Ação.
        Separe os 10 roteiros apenas com o símbolo '###'.
        """
        raw_roteiros = gerar_ia(prompt_roteiros).split("###")

        # 3. LOOP DE MONTAGEM (O Coração da V72)
        for i in range(10):
            # Link com Rastreio Cirúrgico (V1-V71)
            link_track = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_base)}&aff_id={aff_id}&sub_id=V{i+1}"
            
            # Legenda com SEO Randômico (V73)
            legenda = f"{random.choice(ganchos)} {produto}! ✨ {' '.join(random.sample(hashtags, 3))}"
            
            # Tratamento do Roteiro (Garante que não venha vazio)
            roteiro_final = raw_roteiros[i].strip() if i < len(raw_roteiros) else "Cena 1: Gancho | Cena 2: Uso | Cena 3: Link na Bio"

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "produto": f"{produto} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": legenda,
                "roteiro": roteiro_final,
                "horario_previsto": horarios[i],
                "status": "PRONTO",
                "versao_nexus": "V73"
            })
        
        # 4. SALVAMENTO BLINDADO
        df_novo = pd.concat([df, pd.DataFrame(novas)], ignore_index=True)
        df_novo.to_csv(DATA_PATH, index=False)
        return True
        
    except Exception as e:
        st.error(f"Erro no Motor de Escala: {e}")
        return False

def dashboard_performance_simples():
    """ Interface de Monitoramento da V71 """
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        col1, col2 = st.columns(2)
        col1.metric("📦 Fila de Postagem", len(df[df["status"]=="PRONTO"]))
        col2.metric("✅ Enviados hoje", len(df[df["status"]=="ENVIADO"]))
        
        st.subheader("📋 Últimas Variações Geradas")
        st.dataframe(df.tail(10), use_container_width=True)
