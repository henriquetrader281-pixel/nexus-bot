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
    horarios = ["11:15", "12:45", "17:30", "18:50", "20:10", "21:30", "22:45", "08:30", "15:00", "19:55"]

    if "shopee.com.br" not in link_base and "shope.ee" not in link_base:
        st.error(f"❌ Erro: O produto '{produto}' não é da Shopee. Use apenas links da Shopee Brasil.")
        return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        prompt_roteiros = f"Crie 10 roteiros curtos (3 cenas) para {produto} no nicho {nicho}. Sem negrito, sem 'PRODUTO:'. Separe por '###'."
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").replace("1.", "").strip()

        for i in range(10):
            link_track = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            legenda = f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}"
            roteiro_raw = res_roteiros[i].strip() if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso | Cena 3: Link"
            
            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": legenda,
                "roteiro": roteiro_raw.replace("*", ""),
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            
            # Garante colunas mínimas
            colunas_obrigatorias = ["data", "horario_previsto", "produto", "link_afiliado", "status", "copy_funil"]
            for col in colunas_obrigatorias:
                if col not in df.columns: df[col] = "---"

            # LÓGICA DA FONTE (Aqui dentro para não dar NameError)
            df['fonte'] = df['link_afiliado'].apply(lambda x: 'Shopee 🟠' if 'shopee' in str(x).lower() else 'Outro ⚪')

            c1, c2 = st.columns(2)
            c1.metric("📦 Na Fila", len(df[df["status"]=="PRONTO"]))
            c2.metric("✅ Postados", len(df[df["status"]=="ENVIADO"]))

            st.subheader("📅 Cronograma de Postagens")
            
            # Ordem de exibição bonita
            ordem = ["data", "horario_previsto", "fonte", "produto", "link_afiliado", "status"]
            
            st.data_editor(
                df[ordem].tail(20),
                column_config={
                    "fonte": st.column_config.TextColumn("Origem", width="small"),
                    "link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")
                },
                disabled=True,
                use_container_width=True,
                hide_index=True
            )
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    else:
        st.info("Aguardando a primeira injeção de produtos...")
