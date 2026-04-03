import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq

DATA_PATH = "dataset_nexus.csv"

# --- FUNÇÃO DE IA INTEGRADA ---
def gerar_ia_interna(prompt):
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
    horarios = ["08:30", "11:15", "12:45", "15:00", "17:30", "18:50", "20:10", "21:30", "22:45", "23:15"]

    # IDENTIFICAÇÃO DE MERCADO (Separado para expansão futura)
    if "shopee.com.br" in link_base or "shope.ee" in link_base:
        mercado = "Shopee 🟠"
    elif "amazon.com" in link_base:
        mercado = "Amazon 🔵"
    elif "mercadolivre.com" in link_base:
        mercado = "M. Livre 🟡"
    else:
        mercado = "Outro ⚪"

    if mercado != "Shopee 🟠":
        st.error(f"❌ Bloqueado: No momento aceitamos apenas Shopee. Detectado: {mercado}")
        return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        prompt_roteiros = f"Aja como TikToker. Crie 10 roteiros curtos (3 cenas) para {produto}. Sem negrito, separe por '###'."
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").replace("1.", "").strip()

        for i in range(10):
            link_track = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": mercado,
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}",
                "roteiro": res_roteiros[i].strip().replace("*", "") if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso",
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Monitor de Escala Nexus")
    
    # --- ÁREA DE INJEÇÃO MANUAL (Arsenal) ---
    with st.expander("➕ Injetar Link Manual (Shopee Only)"):
        c1, c2 = st.columns(2)
        m_nome = c1.text_input("Nome do Produto Manual")
        m_link = c2.text_input("Cole o Link aqui")
        if st.button("🚀 Injetar Manualmente"):
            if m_nome and m_link:
                if aplicar_seo_viral(m_nome, m_link, "Geral"):
                    st.success("Produto Injetado!")
                    st.rerun()

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if "loja" not in df.columns: df["loja"] = "Shopee 🟠"

        c1, c2 = st.columns(2)
        c1.metric("📦 Na Fila", len(df[df["status"]=="PRONTO"]))
        c2.metric("✅ Enviados", len(df[df["status"]=="ENVIADO"]))

        st.data_editor(
            df[["data", "horario_previsto", "loja", "produto", "status", "link_afiliado"]].tail(30),
            column_config={
                "loja": st.column_config.TextColumn("Mercado", width="small"),
                "link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")
            },
            disabled=["data", "loja"],
            use_container_width=True,
            hide_index=True
        )
