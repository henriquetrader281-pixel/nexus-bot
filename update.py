import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os

DATA_PATH = "dataset_nexus.csv"

def aplicar_seo_viral(produto_nome, link_base, preco, nicho):
    hashtags = ["#achadinhos", "#shopeebrasil", "#utilidades", "#comprinhas", "#viral"]
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    horarios = ["11:15", "12:45", "17:30", "18:50", "20:10", "21:30", "22:45", "08:30", "15:00", "19:55"]

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        df = pd.read_csv(DATA_PATH)
        novas = []

        for i in range(10):
            link_track = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_base)}&aff_id={aff_id}&sub_id=V{i+1}"
            legenda = f"{random.choice(ganchos)} {produto_nome}! ✨ {' '.join(random.sample(hashtags, 3))}"
            
            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "produto": f"{produto_nome} [V{i+1}]",
                "preco": preco,
                "link_afiliado": link_track,
                "copy_funil": legenda,
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except: return False

def dashboard_performance_simples():
    st.subheader("📊 Métricas de Escala")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.metric("Variações Prontas", len(df[df["status"]=="PRONTO"]))
        st.dataframe(df.tail(10))
