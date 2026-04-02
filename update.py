import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq # Importamos a Groq direto aqui para evitar a briga com o app.py

DATA_PATH = "dataset_nexus.csv"

# --- FUNÇÃO DE IA INDEPENDENTE (Evita Erro de Importação Circular) ---
def gerar_ia_update(prompt):
    try:
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

def aplicar_seo_viral(produto, link_base, nicho):
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    hashtags = ["#achadinhos", "#shopee", "#viral", "#utilidades", "#comprinhas"]
    horarios = ["11:15", "12:45", "17:30", "18:50", "20:10", "21:30", "22:45", "08:30", "15:00", "19:55"]

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        # Usamos a função local agora
        prompt_roteiros = f"Crie 10 roteiros ultra-curtos (3 cenas cada) para TikTok sobre {produto} no nicho {nicho}. Separe por '###'."
        res_raw = gerar_ia_update(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        for i in range(10):
            link_track = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_base)}&aff_id={aff_id}&sub_id=V{i+1}"
            legenda = f"{random.choice(ganchos)} {produto}! ✨ {' '.join(random.sample(hashtags, 3))}"
            roteiro_final = res_roteiros[i].strip() if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso | Cena 3: Link"

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "produto": f"{produto} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": legenda,
                "roteiro": roteiro_final,
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Update: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.metric("📦 Fila de Postagem", len(df[df["status"]=="PRONTO"]))
        st.dataframe(df.tail(10), use_container_width=True)
